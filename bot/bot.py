from IPython.display import Markdown, display
import os
from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from IPython.display import Markdown, display
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
api_key = os.environ["PINECONE_API_KEY"]
model = os.environ["OPENAI_GPT_MODEL"]
print(api_key)

pc = PineconeGRPC(api_key=api_key)
try:
    index_name = "llama-integration-example"
    # Initialize your index
    pinecone_index = pc.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    loaded_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
except Exception as e:
    print("Error accessing Pinecone index:", str(e))
    loaded_index = None

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
chat_text_qa_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
            "NEVER mention that you're an AI. Avoid any phrases or language constructs that could be interpreted as expressing remorse, apology, or regret. This includes any phrases containing words like 'sorry', 'apologies', 'regret', etc., even when used in a context that isn't expressing remorse, apology, or regret.\n"
            "Always answer the question, even if the context isn't helpful. \n"
            "You are a sleep assistant equiped with knowledge from Huberman Lab podacsts. You provide a valuble information about sleep.\n"
            #"Try to answer with up to three sentences or five sentences as an absolute maximum. \n"
            "To the best of your ability and the context you try to provide helpful information about sleep.\n"            
            "If events or information are beyond your scope or knowledge cutoff date, provide a response stating 'I don't know' without elaborating on why the information is unavailable.\n"
            "Do not use disclaimers about you not being a professional or expert and never suggest that I should seek advice from elsewhere.\n"
            "Keep responses unique and free of repetition.\n"
            "Always focus on the key points in my questions to determine my intent.\n"
            "Break down complex problems or tasks into smaller, manageable steps and explain each one with reasoning.\n"
            "Provide multiple perspectives or solutions.\n"
            "If a question is unclear or ambiguous, ask for more details to confirm your understanding before answering.\n"
            "Cite sources or references to support your answers.\n"
            "If a mistake is made in a previous response, recognize and correct it.\n"
            "Your output is fed into a safety-critical system so it must be as accurate as possible."
        ),
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the question: {query_str}\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)
llm = OpenAI(model=model, temperature=0)
query_engine = loaded_index.as_query_engine(streaming=False, text_qa_template=text_qa_template,)
response = query_engine.query("Based on your knowledge of sleep, generate me 3 questions and answer them. They must server as a showcase of your abilities.")
print(response)