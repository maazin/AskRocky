# config.py
import os


class Config:
    # Prefer environment variables; leave empty strings as fallback so runtime can detect and prompt
    PINECONE_API = os.getenv("PINECONE_API_KEY", os.getenv("PINECONE_API", ""))
    PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", os.getenv("PINECONE_ENV", "us-east-1"))
    # Optional explicit serverless index host for Pinecone v3+
    PINECONE_HOST = os.getenv("PINECONE_HOST", "")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "bullbot")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PROMPT_TEMPLATE = (
        "You are a chatbot designed to assist users, including students, parents, teachers, and faculty, with queries related to University of South Florida. "
        "The chatbot has information scraped from the school's website and should provide responses based on that data. The bot's tone should be friendly and approachable, "
        "aiming to be as helpful as possible to users. The objective is to make sure all users get accurate and comprehensive answers to their questions about the school. "
        "However, you should not firmly response without have clear and certain evidence in the resources."
    )
