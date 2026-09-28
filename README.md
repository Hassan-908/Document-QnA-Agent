# Document Q&A Agent

An agentic document question-answering application built with **Python, FastAPI, LangChain, Chroma, Hugging Face embeddings, and Groq**.

Unlike a traditional RAG chatbot that always follows a fixed retrieval pipeline, this project uses a LangChain agent that can decide which tools are required to answer a user's question.

The agent can:

- Search information from uploaded PDF documents using RAG
- Perform mathematical calculations
- Call a real external REST API for current weather information
- Chain multiple tools when a question requires more than one source
- Return a final answer based on the collected tool results

## Demo

### Streamlit Interface

The Streamlit interface provides a simple way to upload a PDF and interact with the document Q&A agent.

<img width="1521" height="815" alt="image" src="https://github.com/user-attachments/assets/f02d3705-46d3-4e30-b02c-ce815d6f4cd3" />


### FastAPI Documentation

The backend exposes REST endpoints through FastAPI and provides interactive API documentation through Swagger UI.

<img width="1424" height="605" alt="image" src="https://github.com/user-attachments/assets/2f7e1ae2-acf9-40f0-9421-a3872b8d3092" />


## Architecture

```text
                         User
                           |
                           v
                    Streamlit UI
                           |
                           v
                      FastAPI
                     /       \
                    /         \
               /upload       /ask
                  |             |
                  v             v
             PDF Processing   LangChain Agent
                  |             |
            +-----+-----+       +---------+---------+
            |           |       |         |         |
         Loader      Splitter  RAG    Calculator  Weather
            |           |       |         |         |
            +-----+-----+       |         |         |
                  |             |         |         |
                  v             |         |      Open-Meteo
          HuggingFace           |         |
           Embeddings           |         |
                  |             |         |
                  v             |         |
          Persistent Chroma <---+---------+
                  |
                  v
             Tool Results
                  |
                  v
              Groq LLM
                  |
                  v
             Final Answer
```

## How It Works

### Document Ingestion

When a PDF is uploaded:

```text
PDF
 ↓
PyPDFLoader
 ↓
RecursiveCharacterTextSplitter
 ↓
Hugging Face Embeddings
 ↓
Persistent Chroma
```

The generated embeddings are stored in a persistent Chroma database so documents do not need to be re-embedded for every question.

### Agent Execution

When a question is submitted:

```text
User Question
      ↓
LangChain Agent
      ↓
Choose required tool(s)
      ↓
Tool execution
      ↓
Tool results
      ↓
Groq LLM
      ↓
Final Answer
```

Available tools:

| Tool | Purpose |
|---|---|
| `search_documents` | Searches uploaded documents using Chroma |
| `calculate` | Performs mathematical calculations |
| `get_weather` | Retrieves current weather through Open-Meteo |

The agent can use multiple tools for a single request.

For example:

```text
"What does the document say about ISO 27001
and what is the current weather in Mumbai?"
```

can result in:

```text
search_documents
       ↓
get_weather
       ↓
final answer
```

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### LLM & Agent
- LangChain
- LangChain Groq
- Groq
- `openai/gpt-oss-20b`

### RAG
- Chroma
- LangChain Chroma integration
- Hugging Face Embeddings
- `sentence-transformers/all-MiniLM-L6-v2`
- PyPDF

### API Integration
- Python Requests
- Open-Meteo REST API

### Frontend
- Streamlit

## Project Structure

```text
document-qa-agent/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── model.py
│   │
│   ├── rag/
│   │   ├── loader.py
│   │   ├── splitter.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   │
│   ├── tools/
│   │   ├── document_search.py
│   │   ├── calculator.py
│   │   └── external_api.py
│   │
│   ├── agent/
│   │   └── agent.py
│   │
│   ├── routes/
│   │   ├── upload.py
│   │   └── ask.py
│   │
│   └── main.py
│
├── data/
│   └── uploads/
│
├── chroma_db/
│
├── streamlit_app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## API

### Upload Document

```http
POST /upload
```

Accepts a PDF document and processes it into the persistent Chroma vector database.

Example response:

```json
{
  "filename": "iso27001.pdf",
  "pages": 10,
  "chunks": 42,
  "status": "uploaded"
}
```

### Ask the Agent

```http
POST /ask
```

Request:

```json
{
  "question": "What does the document say about ISO 27001?"
}
```

Example response:

```json
{
  "question": "What does the document say about ISO 27001?",
  "answer": "The document describes...",
  "tools_used": [
    "search_documents"
  ]
}
```

The response also exposes the tools used during agent execution, making the agent workflow easier to inspect during development and testing.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Hassan-908/document-qa-agent.git
cd document-qa-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

`.env` should not be committed to the repository.

### 5. Start FastAPI

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start Streamlit

In a second terminal:

```bash
streamlit run streamlit_app.py
```

Streamlit will be available at:

```text
http://localhost:8501
```

## Example Queries

### Document Search

```text
What does the document say about ISO 27001?
```

Uses:

```text
search_documents
```

### Calculator

```text
What is 125 * 48?
```

Uses:

```text
calculate
```

### External API

```text
What is the current weather in Mumbai?
```

Uses:

```text
get_weather
```

### Multi-Tool Query

```text
What does the document say about ISO 27001
and what is the current weather in Mumbai?
```

Uses multiple tools before generating the final response.

## Key Design Decisions

### Persistent Vector Store

Chroma is configured with a persistent storage directory so document embeddings remain available between API requests and application restarts.

### Agent-Based Tool Selection

Document retrieval is exposed as a LangChain tool rather than being executed automatically for every question. This allows the LLM to decide when retrieval is necessary.

### Real REST API Integration

The weather tool uses Python `requests` to communicate with the Open-Meteo API rather than using a mocked response.

### Separation of Responsibilities

The application separates:

- API routes
- RAG components
- LLM configuration
- Agent configuration
- Tool implementations
- Application configuration

This keeps the project relatively small while making the individual components easier to understand and modify.

## Limitations

This project is designed as a practical demonstration of agentic RAG and API integration rather than a production-ready platform.

Current limitations include:

- PDF documents are the supported document format
- No authentication or authorization
- No user-specific document isolation
- Basic error handling
- Local Chroma persistence
- No advanced observability or tracing
- No document deletion interface

These can be addressed depending on production requirements.

## Future Improvements

Potential improvements include:

- Support for additional document formats
- Document management and deletion
- Metadata-based filtering
- Improved retrieval evaluation
- Streaming responses
- Authentication and user-specific knowledge bases
- Structured logging and monitoring
- More external API tools
- Background document ingestion

## License

This project is intended for learning, experimentation, and demonstration of practical LLM/agent application development.
