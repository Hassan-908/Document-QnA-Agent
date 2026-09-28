from langchain.tools import tool

from app.rag.vector_store import vector_store


@tool
def search_documents(query: str) -> str:
    """
    Search the uploaded documents for information relevant to the user's query.

    Use this tool when the user asks about information contained in the
    uploaded documents.

    If the returned information is not relevant, do not repeatedly search
    the same topic.
    """

    try:
        print(f">>> DOCUMENT SEARCH: {query}")

        results = vector_store.similarity_search_with_relevance_scores(
            query,
            k=4,
        )

        if not results:
            return (
                "No relevant information was found in the uploaded documents. "
                "Do not search again for the same query."
            )

        # Only keep reasonably relevant results.
        relevant_results = [
            (document, score)
            for document, score in results
            if score >= 0.25
        ]

        if not relevant_results:
            return (
                "No sufficiently relevant information was found in the "
                "uploaded documents. Do not search again for the same query."
            )

        output = []

        for document, score in relevant_results:

            source = document.metadata.get(
                "original_filename",
                document.metadata.get("source", "unknown")
            )

            page = document.metadata.get("page")

            if page is not None:
                page = page + 1

            header = f"Source: {source}"

            if page is not None:
                header += f", Page: {page}"

            output.append(
                f"{header}\n"
                f"Relevance score: {score:.2f}\n"
                f"{document.page_content}"
            )

        return "\n\n---\n\n".join(output)

    except Exception as exc:
        return f"Document search failed: {exc}"