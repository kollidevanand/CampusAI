# RAG Chatbot (Niche Domain)

A retrieval-augmented generation (RAG) chatbot that answers questions grounded in
your own documents. Swap the sample college FAQ for legal docs, product manuals,
internal wikis, finance guides — whatever your niche domain is.

## How it works

```
documents (.txt/.md/.pdf)
        │
        ▼
   chunk_text()              (ingest.py)
        │
        ▼
  sentence-transformers       embed each chunk locally (all-MiniLM-L6-v2)
        │
        ▼
     ChromaDB                 persistent local vector store
        │
        │   ◄── user query embedded the same way
        ▼
  top-k similar chunks retrieved   (rag_engine.py)
        │
        ▼
  Claude API (with retrieved      grounded answer, cites sources
  chunks injected as context)
        │
        ▼
    Streamlit UI                  (app.py) chat interface
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your API key**
   ```bash
   cp .env.example .env
   # then edit .env and add your ANTHROPIC_API_KEY
   ```
   Get a key at https://console.anthropic.com

3. **Add your documents**
   Drop `.txt`, `.md`, or `.pdf` files into the `data/` folder. A sample
   `sample_college_faq.txt` is included so you can test immediately.

4. **Ingest documents** (run this any time you add/change documents)
   ```bash
   python ingest.py
   ```

5. **Launch the chatbot**
   ```bash
   streamlit run app.py
   ```
   Opens at `http://localhost:8501`

## Project structure

```
rag-chatbot/
├── data/                 # put your source documents here
│   └── sample_college_faq.txt
├── chroma_db/            # auto-created: persistent vector store
├── ingest.py             # loads, chunks, embeds, stores documents
├── rag_engine.py         # retrieval + Claude API logic
├── app.py                # Streamlit chat UI
├── requirements.txt
└── .env.example
```

## Customizing for your niche domain

- **Change the domain**: replace files in `data/` with your own documents (e.g.
  a legal contract library, a personal finance knowledge base, internal company
  docs) and re-run `python ingest.py`.
- **Tune chunk size**: in `ingest.py`, `CHUNK_SIZE` and `CHUNK_OVERLAP` control
  how documents are split. Smaller chunks → more precise retrieval but less
  context per chunk; larger chunks → more context but noisier retrieval.
- **Tune retrieval depth**: in `rag_engine.py`, `TOP_K` controls how many chunks
  are retrieved per query. Increase it for broad/complex questions, decrease
  for narrow FAQ-style domains.
- **Swap the LLM**: `rag_engine.py` calls `claude-sonnet-4-6` — swap the model
  string or provider if you want to compare against another LLM.
- **Swap the vector DB**: ChromaDB is used here for zero-setup local storage;
  for production scale, swap in Pinecone, Weaviate, or Qdrant.

## Extending this project (good talking points for interviews/portfolio)

- Add **re-ranking** (e.g. a cross-encoder) after initial retrieval to improve
  relevance beyond raw embedding similarity.
- Add **hybrid search** (keyword/BM25 + vector search) for queries with exact
  terms (IDs, names, codes) that embeddings alone handle poorly.
- Add **evaluation**: a small test set of Q&A pairs to measure retrieval
  precision/recall and answer faithfulness (does the answer stay grounded?).
- Add **streaming responses** in the UI using Claude's streaming API.
- Add **citation highlighting**: show the exact retrieved chunk text, not just
  the source filename, so users can verify answers.

## Notes

- Embeddings run **locally** (sentence-transformers) — no API cost for
  ingestion or retrieval, only the final Claude generation call costs tokens.
- ChromaDB persists to disk (`chroma_db/`), so you don't need to re-ingest
  every time you restart the app — only when documents change.
