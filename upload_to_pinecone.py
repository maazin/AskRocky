#!/usr/bin/env python3
"""
Upload data to Pinecone index
Run this AFTER you've created the 'bullbot' index in Pinecone console
"""

import json
import sys
import os

# Add the flaskServer directory to the path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flaskServer'))

from config import Config
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import time

def main():
    print("🚀 Starting data upload to Pinecone...")
    print()
    
    # Initialize Pinecone with the new serverless API
    print("📡 Connecting to Pinecone...")
    print(f"   Index name: {Config.PINECONE_INDEX}")
    
    try:
        # For new pinecone-client (3.0+), use Pinecone class
        pc = Pinecone(api_key=Config.PINECONE_API)
        
        # Check if index exists
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        print(f"   Available indexes: {index_names}")
        
        if Config.PINECONE_INDEX not in index_names:
            print(f"\n❌ Error: Index '{Config.PINECONE_INDEX}' not found!")
            print("\nPlease create the index first:")
            print("   1. Go to https://app.pinecone.io/")
            print("   2. Click 'Create Index'")
            print(f"   3. Name: {Config.PINECONE_INDEX}")
            print("   4. Dimensions: 384")
            print("   5. Metric: cosine")
            print("   6. Cloud: AWS, Region: us-east-1")
            return
        
        print(f"✅ Found index '{Config.PINECONE_INDEX}'")
        
        # Connect to the index
        index = pc.Index(Config.PINECONE_INDEX)
        
        # Check current stats
        try:
            stats = index.describe_index_stats()
            print(f"   Current vector count: {stats.get('total_vector_count', 0)}")
            
            if stats.get('total_vector_count', 0) > 0:
                response = input("\n⚠️  Index already has data. Continue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    print("Aborted.")
                    return
        except Exception as e:
            print(f"   Warning: Could not get index stats: {e}")
        
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {e}")
        print("\nMake sure you've created the index in the Pinecone console first!")
        return
    
    # Load the cleaned data
    print("\n📂 Loading cleaned data...")
    data_path = os.path.join(os.path.dirname(__file__), "Dataset-Pineline", "cleaned_data.json")
    
    if not os.path.exists(data_path):
        print(f"❌ Error: cleaned_data.json not found at {data_path}")
        print("   Please make sure the data file exists")
        return
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} documents")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Initialize embedding model
    print("\n🤖 Loading embedding model (BAAI/bge-small-en-v1.5)...")
    print("   This may take a minute on first run...")
    try:
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Process and upload data in batches
    print("\n📤 Uploading vectors to Pinecone...")
    batch_size = 100
    total_docs = len(data)
    uploaded_count = 0
    
    try:
        for i in range(0, total_docs, batch_size):
            batch = data[i:i + batch_size]
            
            # Prepare vectors
            vectors = []
            for j, doc in enumerate(batch):
                doc_id = f"doc_{i+j}"
                text = doc.get('page_content', '')
                
                if not text:
                    print(f"   Warning: Empty document at index {i+j}, skipping")
                    continue
                
                # Generate embedding
                try:
                    embedding = model.encode(text).tolist()
                except Exception as e:
                    print(f"   Error encoding document {i+j}: {e}")
                    continue
                
                # Prepare metadata
                metadata = doc.get('metadata', {})
                # Truncate text to fit Pinecone metadata limits
                metadata['text'] = text[:1000]
                
                vectors.append({
                    'id': doc_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            if vectors:
                # Upload batch
                try:
                    index.upsert(vectors=vectors)
                    uploaded_count += len(vectors)
                    print(f"   Uploaded {uploaded_count}/{total_docs} documents ({(uploaded_count/total_docs)*100:.1f}%)")
                except Exception as e:
                    print(f"   Error uploading batch: {e}")
                    continue
        
        print(f"\n✅ Upload complete! Uploaded {uploaded_count} documents")
        
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        return
    
    # Verify upload
    print("\n📊 Verifying upload...")
    try:
        time.sleep(2)  # Give Pinecone a moment to update stats
        stats = index.describe_index_stats()
        print(f"   Total vectors in index: {stats.get('total_vector_count', 'unknown')}")
        print(f"   Index dimension: {stats.get('dimension', 'unknown')}")
    except Exception as e:
        print(f"   Warning: Could not verify stats: {e}")
    
    print("\n🎉 Data upload complete!")
    print("\nNext steps:")
    print("   1. Start Flask server: cd flaskServer && python app.py")
    print("   2. Start Express server: cd server && npm start")
    print("   3. Start Vite client: cd client && npm run dev")
    print("   4. Open http://localhost:5173 in your browser")

if __name__ == "__main__":
    main()
