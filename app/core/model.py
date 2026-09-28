from langchain_groq import ChatGroq

from app.core.config import GROQ_API_KEY, GROQ_MODEL


model = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0,
)