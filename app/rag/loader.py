from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path: Path):
    loader = PyPDFLoader(str(file_path))

    documents = loader.load()

    return documents