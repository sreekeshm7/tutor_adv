# groq_config.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()  # Load environment variables from .env

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file or environment variables.")
    
    return ChatGroq(
        model="Llama3-70B",
        api_key=api_key

    )

