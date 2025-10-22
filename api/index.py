from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
import threading

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'flaskServer'))

from config import Config
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models.openai import ChatOpenAI
from pinecone import Pinecone

app = Flask(__name__)
CORS(app)  # Enable CORS for Vercel deployment
app.config.from_object(Config)

# Set environment variables for Langchain
os.environ["OPENAI_API_KEY"] = app.config['OPENAI_API_KEY']
os.environ["PINECONE_API_KEY"] = app.config['PINECONE_API']
os.environ["PINECONE_ENVIRONMENT"] = app.config['PINECONE_ENV']

EMBEDDINGS_MODEL = None
PINE_CONE = None
READY = False

@app.route('/')
def home():
    return jsonify({'message': 'Bull Bot API is running'}), 200

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

        result = retrieve(prompt, docsearch, llm_model)
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

def embeddings():
    """bge embeddings models from huggingface. Dimensions: 384"""
    global EMBEDDINGS_MODEL

    if EMBEDDINGS_MODEL is None:
        print("Loading Embeddings Model...")
        model_name = "BAAI/bge-small-en-v1.5"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        EMBEDDINGS_MODEL = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    return EMBEDDINGS_MODEL

def pineconeInitialization(embeddings):
    """Initialize Pinecone vector store"""
    global PINE_CONE
    
    if PINE_CONE is None:
        print("[INIT] Initializing Pinecone vector store...")
        try:
            from langchain_pinecone import PineconeVectorStore
            from pinecone import Pinecone as PineconeClient
            
            index_name = app.config['PINECONE_INDEX']
            print(f"[INIT] Connecting to Pinecone index: {index_name}")
            
            # Initialize Pinecone client and get the index
            pc = PineconeClient(api_key=app.config['PINECONE_API'])
            pinecone_index = pc.Index(index_name)
            
            # Use the new langchain-pinecone package
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

def retrieve(query, docsearch, llm):
    """Retrieve and generate answer"""
    prompt_template = app.config['PROMPT_TEMPLATE'] + """
    
    Context: {context}
    
    Question: {question}
    Helpful Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    chain_type_kwargs = {"prompt": PROMPT}
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True
    )
    
    result = qa({"query": query})
    return result

# For Vercel serverless
if __name__ == '__main__':
    # Preload heavy resources in a background thread so first requests don't block
    def _warmup():
        global READY
        try:
            print("[BOOT] Preloading embeddings and Pinecone...")
            emb = embeddings()
            pineconeInitialization(emb)
            READY = True
            print("[BOOT] Preload complete. System READY.")
        except Exception as e:
            print(f"[BOOT] Preload failed: {e}")

    threading.Thread(target=_warmup, daemon=True).start()
    # Run Flask without the reloader to simplify logging and stability
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
