from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
import threading

# stdout is fully block-buffered when it isn't a tty (true under gunicorn),
# so plain print() calls can sit unflushed for minutes -- exactly what made
# the fastembed startup hang below look silent while it was happening.
# Line-buffer it so boot/debug logs show up as they're printed.
sys.stdout.reconfigure(line_buffering=True)

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'flaskServer'))

from config import Config
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.prompts import PromptTemplate
# Compatible import for langchain==0.0.291
from langchain.chat_models import ChatOpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for Vercel deployment
app.config.from_object(Config)

# Debug: confirm config values are loaded (do not print secrets; only lengths)
try:
    pine_api_val = app.config.get('PINECONE_API')
    openai_val = app.config.get('OPENAI_API_KEY')
    print(f"[DEBUG] Config PINECONE_API present: {pine_api_val is not None}, length: {len(pine_api_val) if pine_api_val else 0}")
    print(f"[DEBUG] Config OPENAI_API_KEY present: {openai_val is not None}, length: {len(openai_val) if openai_val else 0}")
except Exception:
    print("[DEBUG] Unable to read config values")

# Set environment variables for Langchain and Pinecone (only if provided)
cfg_openai = app.config.get('OPENAI_API_KEY')
cfg_pine_api = app.config.get('PINECONE_API')
cfg_pine_env = app.config.get('PINECONE_ENV')

if cfg_openai:
    os.environ["OPENAI_API_KEY"] = cfg_openai
else:
    # If not in config, try to pull into config from environment
    env_openai = os.getenv("OPENAI_API_KEY")
    if env_openai:
        app.config['OPENAI_API_KEY'] = env_openai

if cfg_pine_api:
    os.environ["PINECONE_API_KEY"] = cfg_pine_api
else:
    env_pine = os.getenv("PINECONE_API_KEY") or os.getenv("PINECONE_API")
    if env_pine:
        app.config['PINECONE_API'] = env_pine
        os.environ["PINECONE_API_KEY"] = env_pine

if cfg_pine_env:
    os.environ["PINECONE_ENVIRONMENT"] = cfg_pine_env
else:
    env_penv = os.getenv("PINECONE_ENVIRONMENT") or os.getenv("PINECONE_ENV")
    if env_penv:
        app.config['PINECONE_ENV'] = env_penv
        os.environ["PINECONE_ENVIRONMENT"] = env_penv

EMBEDDINGS_MODEL = None
PINE_CONE = None
READY = False
EXPECTED_EMBED_DIM = 384
EXPECTED_METRIC = "cosine"

@app.route('/')
def home():
    return jsonify({'message': 'AskRocky API is running'}), 200

@app.route('/health', methods=['GET'])
def health():
    """Simple readiness probe."""
    return jsonify({'status': 'ok', 'ready': READY}), 200

@app.route('/api', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - compatible with client script.js"""
    data = request.get_json()
    
    # Accept both 'prompt' (from client) and 'input' (from original)
    prompt = data.get('prompt') or data.get('input')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        start_ts = time.time()
        print(f"[API] Received prompt: {prompt}")
        # If system not ready, serve a quick non-RAG response
        if EMBEDDINGS_MODEL is None or PINE_CONE is None:
            print("[API] System not fully ready. Serving non-RAG fallback response.")
            llm_model = llm_LOAD('gpt-3.5-turbo-16k', 500, 0.5)
            fallback_prompt = (
                "You are a helpful assistant for the University of South Florida (USF). "
                "Answer concisely based on your general knowledge. Mention that the knowledge base is still loading.\n\n"
                f"User question: {prompt}"
            )
            ai = llm_model.predict(fallback_prompt)
            resp = jsonify({
                'bot': {
                    'result': ai + "\n\n(Note: Knowledge base is still loading; answers will improve shortly.)",
                    'title': [],
                    'source': []
                }
            })
            dur = (time.time() - start_ts)
            print(f"[API] Fallback responded in {dur:.2f}s")
            return resp, 200

        embeddingModel = EMBEDDINGS_MODEL  # already initialized
        print("[API] Embeddings loaded successfully")

        docsearch = pineconeInitialization(embeddingModel)
        print("[API] Pinecone initialized successfully")

        llm_model = llm_LOAD('gpt-3.5-turbo-16k', 500, 0.5)
        print("[API] LLM loaded successfully")

        # Use direct similarity search to avoid retriever API incompatibilities
        result = retrieve_simple(prompt, docsearch, llm_model)
        print("[API] Retrieved result from LLM")

        answer = result['result']
        source = [result['source_documents'][i].metadata['source'] for i in range(len(result['source_documents']))]

        for doc in result['source_documents']:
            if 'title' not in doc.metadata:
                doc.metadata['title'] = 'No Title'

        titles = [result['source_documents'][i].metadata['title'] for i in range(len(result['source_documents']))]

        # Return in format expected by client
        resp = jsonify({
            'bot': {
                'result': answer,
                'title': titles,
                'source': source
            }
        })
        dur = (time.time() - start_ts)
        print(f"[API] Responding OK in {dur:.2f}s")
        return resp, 200
        
    except Exception as e:
        print(f"[API] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'{str(e)}'}), 500

class FastEmbedEmbeddings(Embeddings):
    """
    Runs BAAI/bge-small-en-v1.5 through fastembed (ONNX runtime) instead of
    sentence-transformers (PyTorch). Same model weights, so vectors are
    compatible with what's already indexed in Pinecone -- but the torch +
    transformers stack this replaces was the actual cause of the OOM kills
    on Render's free 512MB tier, so this is what makes the free tier viable.

    Pinecone's index metric is cosine, which is scale-invariant, so a query
    vector doesn't need to be normalized the same way the indexed vectors
    were to retrieve correctly.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding

        # onnxruntime sizes its intra-op thread pool off the HOST's CPU count,
        # not the cgroup quota a container is actually given. On Render's free
        # tier (0.1 vCPU) that oversized pool gets starved by the throttle and
        # session build can hang for a very long time instead of erroring.
        # Pin it small; a model this size doesn't benefit from more threads
        # anyway. Override with FASTEMBED_THREADS if a bigger instance
        # warrants it.
        threads = int(os.getenv("FASTEMBED_THREADS", "2"))
        self._model = TextEmbedding(model_name=model_name, threads=threads)

    def embed_documents(self, texts):
        return [vector.tolist() for vector in self._model.embed(texts)]

    def embed_query(self, text):
        return next(iter(self._model.embed([text]))).tolist()


def embeddings():
    """BAAI/bge-small-en-v1.5 embeddings via fastembed. Dimensions: 384"""
    global EMBEDDINGS_MODEL

    if EMBEDDINGS_MODEL is None:
        print("Loading Embeddings Model...")
        EMBEDDINGS_MODEL = FastEmbedEmbeddings()
    return EMBEDDINGS_MODEL

def pineconeInitialization(embeddings):
    """Initialize Pinecone vector store"""
    global PINE_CONE
    
    if PINE_CONE is None:
        print("[INIT] Initializing Pinecone vector store...")
        try:
            from langchain_pinecone import PineconeVectorStore

            index_name = os.getenv('PINECONE_INDEX') or app.config['PINECONE_INDEX']
            print(f"[INIT] Connecting to Pinecone index: {index_name}")

            # Ensure environment variables are set for the pinecone package
            # to pick up; set both PINECONE_API_KEY and fallback names.
            pine_api = app.config.get('PINECONE_API') or os.getenv('PINECONE_API_KEY') or os.getenv('PINECONE_API')
            pine_env = app.config.get('PINECONE_ENV') or os.getenv('PINECONE_ENVIRONMENT') or os.getenv('PINECONE_ENV')
            pine_host = app.config.get('PINECONE_HOST') or os.getenv('PINECONE_HOST')
            if pine_api:
                os.environ['PINECONE_API_KEY'] = pine_api
                os.environ['PINECONE_API'] = pine_api
                # Only log key length to avoid leaking secrets
                print(f"[INIT] Pinecone API key length: {len(pine_api)}")
            if pine_env:
                os.environ['PINECONE_ENVIRONMENT'] = pine_env
                os.environ['PINECONE_ENV'] = pine_env

            # Import Pinecone client now that env vars are set
            from pinecone import Pinecone as PineconeClient

            # Create a Pinecone client instance; some pinecone versions also
            # accept the api_key keyword, but env var ensures compatibility.
            if not pine_api:
                raise RuntimeError("Pinecone API key is missing. Set PINECONE_API_KEY in environment or flaskServer/config.py.")
            pc = PineconeClient(api_key=pine_api)

            # Validate index schema if possible (dimension, metric)
            try:
                desc = pc.describe_index(index_name)
                dim = desc.get('dimension') or desc.get('spec', {}).get('dimension')
                metric = desc.get('metric') or desc.get('spec', {}).get('metric')
                if dim and dim != EXPECTED_EMBED_DIM:
                    raise RuntimeError(
                        f"Pinecone index '{index_name}' has dimension {dim}, expected {EXPECTED_EMBED_DIM} for BAAI/bge-small-en-v1.5. "
                        "Please recreate or reconfigure the index."
                    )
                if metric and metric.lower() != EXPECTED_METRIC:
                    raise RuntimeError(
                        f"Pinecone index '{index_name}' metric is '{metric}', expected '{EXPECTED_METRIC}'. "
                        "Please recreate or reconfigure the index (cosine recommended)."
                    )
                print(f"[INIT] ✅ Index schema OK (dim={dim}, metric={metric})")
            except Exception as e:
                # If describe is not available or different client version, log and continue
                print(f"[INIT] (Info) Could not validate index schema automatically: {e}")

            if pine_host:
                print(f"[INIT] Using explicit Pinecone host: {pine_host}")
                pinecone_index = pc.Index(index_name, host=pine_host)
            else:
                pinecone_index = pc.Index(index_name)

            # Wrap the index with langchain-pinecone
            PINE_CONE = PineconeVectorStore(
                index=pinecone_index,
                embedding=embeddings,
                text_key="text"
            )
            print("[INIT] ✅ Pinecone vector store initialized successfully")

        except Exception as e:
            print(f"[INIT] ❌ ERROR initializing Pinecone: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    return PINE_CONE

def llm_LOAD(model, max_tokens, temp):
    """Load OpenAI LLM"""
    llm = ChatOpenAI(
        model_name=model,
        temperature=temp,
        max_tokens=max_tokens,
        request_timeout=60
    )
    return llm

def retrieve_simple(query, vector_store, llm, k: int = 4):
    """Retrieve top-k docs via similarity_search and generate answer with a stuffed prompt.
    Returns a dict compatible with previous result shape: { 'result': str, 'source_documents': [Document, ...] }
    """
    # Fetch relevant documents
    try:
        docs = vector_store.similarity_search(query, k=k)
    except Exception as e:
        # As a fallback if the method name differs, try max_marginal_relevance_search
        try:
            docs = vector_store.max_marginal_relevance_search(query, k=k)
        except Exception:
            raise e

    # Build context
    context = "\n\n".join([d.page_content for d in docs])

    # Compose prompt
    prompt_template = app.config['PROMPT_TEMPLATE'] + """

Context:
{context}

Question: {question}
Helpful Answer:"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )

    final_prompt = PROMPT.format(context=context, question=query)
    answer = llm.predict(final_prompt)

    return {"result": answer, "source_documents": docs}

def _warmup():
    """Load the embedding model and connect to Pinecone."""
    global READY
    try:
        print("[BOOT] Preloading embeddings and Pinecone...")
        emb = embeddings()
        pineconeInitialization(emb)
        READY = True
        print("[BOOT] Preload complete. System READY.")
    except Exception as e:
        print(f"[BOOT] Preload failed: {e}")

_WARMUP_STARTED = False

def start_warmup():
    """Kick off the preload in a background thread so first requests don't block.

    This runs on import, not just under __main__, so WSGI servers (gunicorn on
    Render/Heroku/Railway) warm up too. Without it those deployments would never
    build the vector store and would serve the non-RAG fallback on every request.
    """
    global _WARMUP_STARTED
    if _WARMUP_STARTED:
        return
    _WARMUP_STARTED = True
    threading.Thread(target=_warmup, daemon=True).start()

# Skip the preload under the Flask reloader's parent process, which would
# otherwise load the model twice.
if os.getenv("ASKROCKY_SKIP_WARMUP") != "1":
    start_warmup()

if __name__ == '__main__':
    # Run Flask without the reloader to simplify logging and stability
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
