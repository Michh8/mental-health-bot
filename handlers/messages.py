import logging
from telegram import Update
from telegram.ext import ContextTypes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from config import GEMINI_API_KEY
from utils.tools import tools_list

# Modelo Gemini
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

# Memoria conversacional
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Agente LangChain con las Tools
agent = initialize_agent(
    tools=tools_list,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        response = agent.run(user_message)
        await update.message.reply_text(response)
    except Exception as e:
        logging.exception("Error en chat con agente LangChain")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar tu mensaje.")
