from langchain_chroma import Chroma

from app.core.config import CHROMA_DIR, COLLECTION_NAME
from app.rag.embeddings import embeddings


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)