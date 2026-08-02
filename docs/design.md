# SmartLearn Agent - Product Design

## User Stories

1. As a **student**, I want to **upload a PDF lecture slide and ask questions about it**, so that **I can study more efficiently without flipping through dozens of pages**.

2. As a **student**, I want to **get answers with page numbers**, so that **I can quickly find the original content in the PDF and verify the answer myself**.

3. As a **student**, I want to **ask follow-up questions in a single conversation**, so that **I can deepen my understanding of a topic without starting over each time**.

---

## Feature List

| Priority | Feature | Day |
|----------|---------|-----|
| P0 | PDF text extraction | Day 2 |
| P0 | LLM Q&A with page citation | Day 2 |
| P0 | Web UI (React frontend + FastAPI backend) | Day 2 |
| P1 | RAG pipeline (chunk + embed + similarity search) | Day 3 |
| P1 | Multi-turn conversation memory | Day 3 |
| P2 | Chat history persistence | Day 3 |

## What We Will NOT Build

- **User authentication / login** — workshop time is limited; focus on core AI features
- **Multi-file upload** — perfect the single-PDF experience first
- **Mobile app** — web version only; a responsive UI is sufficient
- **PDF OCR (scanned document support)** — text-based PDFs only; OCR adds complexity and cost
- **Deployment to production** — localhost development only during the workshop

---

## Data Flow

### Day 2: Simple Mode

```
PDF File
  -> [PDF parser / extract text]
  -> pages[]
  -> [build prompt: pages + question]
  -> [LLM]
  -> Answer with [Page X]
```

### Day 3: RAG Mode

```
PDF -> [extract text] -> pages
    -> [split into chunks] -> chunks with source_page
    -> [embed] -> embeddings
    -> [vector store (FAISS)]  # storage

Question -> [encode] -> [similarity search] -> relevant chunks -> [LLM] -> Answer
```
