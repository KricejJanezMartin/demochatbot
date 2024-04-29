from IPython.display import Markdown, display
import os
from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore

api_key = os.environ["PINECONE_API_KEY"]
print(api_key)

pc = PineconeGRPC(api_key=api_key)
index_name = "llama-integration-example"
# Initialize your index
pinecone_index = pc.Index(index_name)