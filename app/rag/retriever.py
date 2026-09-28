from app.core.config import RETRIEVAL_K
from app.rag.vector_store import vector_store


retriever = vector_store.as_retriever(
    search_kwargs={
        "k": RETRIEVAL_K
    }
)