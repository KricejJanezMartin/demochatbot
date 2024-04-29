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
            "Never start the sentence with any mention of the word context or based on the context information provided.\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)
llm = OpenAI(model=model, temperature=0)


query_engine = loaded_index.as_query_engine(streaming=False, text_qa_template=text_qa_template,)
#response = query_engine.query("Based on your knowledge of sleep, give me a short introduction of your capabilities. 2 or 3 sentences")
#print(response)

from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, \
    CallbackQueryHandler
from telegram.constants import ChatAction
import asyncio
import os

TOKEN: Final = os.environ["TELEGRAM_TOKEN"]
BOT_USERNAME: Final = os.environ["BOT_USERNAME"]
#Commands
#Pozdrav ko nekdo pritisne Start:
async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "Hello! I am a sleep bot expert.\n"
        "My commands are avaliable to you under the Menu button on the left side next to chat input.\n"
        "You can ask me anything about sleep and I will try to provide you with the best answer.\n"
    )

# /help commanda (tu bomo listali vse komande)
async def help_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Here are my commands: \n "
    "/start - Starts the bot\n "
    "/help - Provide help for our bot\n "
    "/huberman - Redirect to Huberman Lab podcast page\n")

async def huberman_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To listen to Huberman Lab podcast visit: https://hubermanlab.com/")

def generate_response(user_message: str) -> str:
    print("User wrote:", user_message)
    #response = query_engine.query(user_message)
    response = query_engine.query(user_message) 
    response_str = str(response)
    return response_str

async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type}: "{text}"')
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=update.message.chat.id, action=ChatAction.TYPING)

    #preverimo ali je chat v groupi ali v 1:1 chatu
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()

            response: str = generate_response(new_text) #  handle_response(new_text)
        #Će ga nena taggađ v grupi se nebo odzval
        else:
            return
    #To je pa za 1:1 chat
    else:

        response: str = generate_response(text) #Stara metoda: handle_response(text)
    print('Bot:', response) #loganje

    #Vrneš potem response userju
    await update.message.reply_text(response)

async def error(update:Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

print("Bot recieved commands")

if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start', start_command)) #Specificiraš keri je start command pa  na kero metodo gre
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('huberman', huberman_command))
    #app.add_handler(CommandHandler('wh2c', wh2c_command))
    #app.add_handler(CommandHandler('join', join_command))
    #app.add_handler(CommandHandler('lightpaper', lightpaper_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT,handle_message))

    #Errors
    app.add_error_handler(error)

    #Preverjanje za nove update-e
    print("Polling")
    app.run_polling(poll_interval=3) #vsake 3 sekunde
