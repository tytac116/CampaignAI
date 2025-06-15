"""
Create Pinecone Index Script

This script creates a Pinecone index for campaign data vector storage.
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

def create_pinecone_index():
    """Create Pinecone index for campaign data."""
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    
    index_name = "campaign-optimization"
    
    # Check if index already exists
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"✅ Index '{index_name}' already exists!")
        return
    
    print(f"🔧 Creating Pinecone index: {index_name}")
    
    # Create index with serverless spec
    pc.create_index(
        name=index_name,
        dimension=1536,  # text-embedding-3-small dimensions
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    
    print(f"✅ Successfully created index: {index_name}")
    print(f"📊 Dimensions: 1536")
    print(f"📏 Metric: cosine")
    print(f"☁️  Type: serverless (AWS us-east-1)")

if __name__ == "__main__":
    create_pinecone_index() 