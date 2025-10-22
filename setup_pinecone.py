#!/usr/bin/env python3
"""
Setup script to create Pinecone index and upload data
"""

import json
import sys
import os
import pinecone
from sentence_transformers import SentenceTransformer
import time

# Configuration (read from environment)
PINECONE_API_KEY = os.getenv("PINECONE_API", "")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
INDEX_NAME = os.getenv("PINECONE_INDEX", "bullbot")
DIMENSION = 384  # BGE-small-en-v1.5 produces 384-dimensional embeddings

def main():
    print("🚀 Starting Pinecone setup...")
    
    # Initialize Pinecone
    print("📡 Connecting to Pinecone...")
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API is not set in the environment.")
        print("   Please set PINECONE_API (and optionally PINECONE_ENV, PINECONE_INDEX) before running.")
        sys.exit(1)
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    
    # Check if index exists
    existing_indexes = pinecone.list_indexes()
    
    if INDEX_NAME in existing_indexes:
        print(f"✅ Index '{INDEX_NAME}' already exists")
        index = pinecone.Index(INDEX_NAME)
        stats = index.describe_index_stats()
        print(f"   Current vector count: {stats['total_vector_count']}")
        
        if stats['total_vector_count'] > 0:
            response = input("⚠️  Index already has data. Do you want to delete and recreate it? (yes/no): ")
            if response.lower() != 'yes':
                print("✅ Using existing index")
                return
            print("🗑️  Deleting existing index...")
            pinecone.delete_index(INDEX_NAME)
            time.sleep(5)  # Wait for deletion to complete
    
    # Create new index
    print(f"📦 Creating new index '{INDEX_NAME}'...")
    pinecone.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric='cosine'
    )
    
    # Wait for index to be ready
    print("⏳ Waiting for index to be ready...")
    time.sleep(10)  # Give it some time to initialize
    
    print("✅ Index created successfully!")
    
    # Load the cleaned data
    print("📂 Loading cleaned data...")
    data_path = "/Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot/Dataset-Pineline/cleaned_data.json"
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} documents")
    except FileNotFoundError:
        print(f"❌ Error: cleaned_data.json not found at {data_path}")
        print("   Please run the data pipeline notebooks first")
        return
    
    # Initialize embedding model
    print("🤖 Loading embedding model (this may take a minute)...")
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    print("✅ Model loaded")
    
    # Connect to index
    index = pinecone.Index(INDEX_NAME)
    
    # Process and upload data in batches
    print("📤 Uploading vectors to Pinecone...")
    batch_size = 100
    total_docs = len(data)
    
    for i in range(0, total_docs, batch_size):
        batch = data[i:i + batch_size]
        
        # Prepare vectors
        vectors = []
        for j, doc in enumerate(batch):
            doc_id = f"doc_{i+j}"
            text = doc['page_content']
            
            # Generate embedding
            embedding = model.encode(text).tolist()
            
            # Prepare metadata
            metadata = doc.get('metadata', {})
            metadata['text'] = text[:1000]  # Store first 1000 chars of text
            
            vectors.append({
                'id': doc_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Upload batch
        index.upsert(vectors=vectors)
        print(f"   Uploaded {min(i + batch_size, total_docs)}/{total_docs} documents")
    
    print("✅ All data uploaded successfully!")
    
    # Verify upload
    stats = index.describe_index_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Total vectors: {stats['total_vector_count']}")
    print(f"   Index dimension: {stats['dimension']}")
    
    print("\n🎉 Pinecone setup complete!")

if __name__ == "__main__":
    main()
