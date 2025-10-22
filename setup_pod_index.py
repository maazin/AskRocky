"""
Create a POD-BASED Pinecone index (compatible with pinecone-client 2.2.4)
and upload the data
"""
import pinecone
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm
import time

# Configuration
API_KEY = "pcsk_6vMft9_UfXEPMt5YpVXYr8XBrVX1uEqA4BfWPAjqN9gxjvvwJm2L2NZ66VqpTMQJwLyj3"
ENVIRONMENT = "us-east-1"  # This will work for starter (free) pod
INDEX_NAME = "bullbot-pod"

def main():
    print("🚀 Setting up Pod-based Pinecone index for Bull Bot...")
    
    # Initialize Pinecone
    pinecone.init(api_key=API_KEY, environment=ENVIRONMENT)
    
    # Check if index exists, delete if it does
    if INDEX_NAME in pinecone.list_indexes():
        print(f"⚠️  Index '{INDEX_NAME}' already exists. Deleting...")
        pinecone.delete_index(INDEX_NAME)
        time.sleep(5)
    
    # Create pod-based index
    print(f"📦 Creating POD-based index '{INDEX_NAME}'...")
    pinecone.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        pod_type="p1.x1"  # Free tier pod
    )
    
    print("⏳ Waiting for index to be ready...")
    time.sleep(10)
    
    # Connect to index
    index = pinecone.Index(INDEX_NAME)
    
    # Load embedding model
    print("🤖 Loading embedding model...")
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    # Load data
    print("📚 Loading data from cleaned_data.json...")
    with open('cleaned_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} documents")
    
    # Upload in batches
    batch_size = 100
    vectors = []
    
    print("⬆️  Uploading to Pinecone...")
    for i, item in enumerate(tqdm(data)):
        # Create embedding
        text = item['text']
        embedding = model.encode(text).tolist()
        
        # Create vector record
        vector_id = f"doc_{i}"
        metadata = {
            'text': text,
            'source': item.get('source', 'unknown')
        }
        
        vectors.append((vector_id, embedding, metadata))
        
        # Upload batch
        if len(vectors) >= batch_size:
            index.upsert(vectors=vectors)
            vectors = []
    
    # Upload remaining vectors
    if vectors:
        index.upsert(vectors=vectors)
    
    print("✅ Upload complete!")
    
    # Verify
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n📊 Index stats:")
    print(f"   Total vectors: {stats['total_vector_count']}")
    print(f"   Dimension: {stats['dimension']}")
    print(f"\n✅ Setup complete! Update your config.py:")
    print(f"   PINECONE_INDEX = '{INDEX_NAME}'")

if __name__ == "__main__":
    main()
