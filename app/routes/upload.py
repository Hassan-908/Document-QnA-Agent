from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import vector_store


router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported."
        )

    # Give every upload a unique stored filename.
    safe_name = Path(file.filename).name
    stored_filename = f"{uuid.uuid4().hex}_{safe_name}"

    file_path = UPLOAD_DIR / stored_filename

    try:
        # ----------------------------------------
        # Save uploaded PDF
        # ----------------------------------------
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ----------------------------------------
        # Load PDF
        # ----------------------------------------
        documents = load_pdf(file_path)

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No readable content found in PDF."
            )

        # ----------------------------------------
        # Split into chunks
        # ----------------------------------------
        chunks = split_documents(documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create document chunks."
            )

        # ----------------------------------------
        # Add chunks to persistent Chroma
        # ----------------------------------------
        ids = []

        for index, chunk in enumerate(chunks):
            chunk.metadata["original_filename"] = safe_name
            chunk.metadata["stored_filename"] = stored_filename

            ids.append(
                f"{stored_filename}_{index}"
            )

        vector_store.add_documents(
            documents=chunks,
            ids=ids,
        )

        return {
            "filename": safe_name,
            "pages": len(documents),
            "chunks": len(chunks),
            "status": "uploaded",
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {exc}"
        )