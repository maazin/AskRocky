from flask import Flask, request, jsonify
from config import Config
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Pinecone
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models.openai import ChatOpenAI
import pinecone


app = Flask(__name__)
app.config.from_object(Config)

import os
os.environ["OPENAI_API_KEY"] = app.config['OPENAI_API_KEY']
@app.route('/')
@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    data = request.get_json()
    if 'input' not in data:
        return jsonify({'error': 'The key in the data should be input.'}), 400
    prompt = data['input']
    
    try:
        embeddingModel = embeddings()
        docsearch = pineconeInitialization(embeddingModel)
        llm_model = llm_LOAD('gpt-3.5-turbo-16k', 500, 0.5)
        result = retrieve(prompt, docsearch, llm_model)
        answer = result['result']
        source = [result['source_documents'][i].metadata['source'] for i in range(len(result['source_documents']))]
        for doc in result['source_documents']:
            if 'title' not in doc.metadata:
                doc.metadata['title'] = 'No Title' 
        titles = [result['source_documents'][i].metadata['title'] for i in range(len(result['source_documents']))]
        return jsonify({'result': answer, 'title': titles ,'source': source}), 200
    except Exception as e:
        return jsonify({'error': f'{e}'}), 400

EMBEDDINGS_MODEL = None
PINE_CONE = None
def embeddings():
    """bge embeddings models from huggingface. Dimensions: 768"""
    global EMBEDDINGS_MODEL

    if EMBEDDINGS_MODEL is None:
        print("Downloading Embeddings...")
        model_name = "BAAI/bge-small-en-v1.5"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        EMBEDDINGS_MODEL = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    print("Embeddings Loaded")
    
    return EMBEDDINGS_MODEL

def pineconeInitialization(embeddings):
    global PINE_CONE

    if PINE_CONE is None:
        print("Initializing PineCone...")
        api_key = app.config['PINECONE_API']
        env = app.config['PINECONE_ENV']
        pinecone.init(api_key=api_key, environment=env)
        print("PineCone initialized")
        index = app.config['PINECONE_INDEX']
        docsearch = Pinecone.from_existing_index(index, embeddings)
    print("Vector Store Loaded")
    return docsearch

def llm_LOAD(model_name = 'gpt-3.5-turbo', max_tokens = 500, temperature=0.5):
    print("Loading Language Model...")
    llm = ChatOpenAI(
    temperature=temperature,
    model_name = model_name,
    max_tokens = max_tokens,
    )
    print("Language Model Loaded")
    return llm

def retrieve(query, docsearch, llm):
    print("Retrieving...")
    prompt_template = app.config['PROMPT_TEMPLATE'] + " \n\n "
    prompt_template += " {context} " + " \n\n "
    prompt_template += " Question: {question} "

    PROMPT = PromptTemplate(template=prompt_template, input_variables=['question', 'context'])

    query = query
    qa_with_sources = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=True ,chain_type_kwargs={"prompt": PROMPT})

    result = qa_with_sources({"query": query})
    return result

def main():
    print('working')

if __name__ == "__main__":
    print("Hello I'm Working")
    app.run(host="0.0.0.0", port=8000, debug=True)
    main()