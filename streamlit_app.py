import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Document Q&A Agent",
    page_icon="📄",
)


st.title("Document Q&A Agent")

st.write(
    "Upload a PDF and ask questions using an agent with "
    "document search, calculations and live weather."
)


# --------------------------------------------------
# Upload
# --------------------------------------------------

st.header("1. Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"],
)


if st.button("Upload PDF"):

    if uploaded_file is None:
        st.warning("Please select a PDF first.")

    else:
        try:
            response = requests.post(
                f"{API_URL}/upload",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                },
                timeout=120,
            )

            if response.ok:
                data = response.json()

                st.success(
                    f"Uploaded {data['filename']} — "
                    f"{data['pages']} pages, "
                    f"{data['chunks']} chunks."
                )

            else:
                st.error(response.text)

        except requests.RequestException as exc:
            st.error(f"Could not connect to FastAPI: {exc}")


# --------------------------------------------------
# Ask
# --------------------------------------------------

st.header("2. Ask the Agent")

question = st.text_input(
    "Question",
    placeholder=(
        "What does the document say about ISO27001?"
    ),
)


if st.button("Ask Agent"):

    if not question.strip():
        st.warning("Enter a question.")

    else:
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={
                    "question": question,
                },
                timeout=120,
            )

            if response.ok:
                data = response.json()

                st.subheader("Answer")

                st.write(data["answer"])

                st.subheader("Tools Used")

                tools = data.get("tools_used", [])

                if tools:
                    for tool in tools:
                        st.code(tool)
                else:
                    st.write("No tools were required.")

            else:
                st.error(response.text)

        except requests.RequestException as exc:
            st.error(f"Could not connect to FastAPI: {exc}")