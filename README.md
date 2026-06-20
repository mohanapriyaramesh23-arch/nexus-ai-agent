# Nexus — Multi-Source Agentic AI System

> An AI agent that answers questions by intelligently searching across PDFs, 
> YouTube, live news, websites, and web search — combining results into one 
> cited, accurate answer.

🔴 **Live Demo** — Coming soon
📹 **Demo Video** — Coming soon

---

## What Nexus Does

Unlike basic RAG chatbots that only query one document, Nexus uses a 
LangGraph agent to decide which sources are relevant to a question, 
retrieves from multiple sources in parallel, and synthesizes one answer 
with full source citations.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM + Embeddings | Google Gemini API (gemini-2.5-flash, gemini-embedding-001) |
| Agent Orchestration | LangGraph |
| Vector Database | Qdrant Cloud |
| Hybrid Retrieval | BM25 + Vector Search + Reciprocal Rank Fusion |
| Frontend | Gradio |
| Backend API | FastAPI |
| Evaluation | RAGAs |
| Report Generation | ReportLab |

---

## Setup

```bash
git clone https://github.com/mohanapriyaramesh23-arch/nexus-ai-agent.git
cd nexus-ai-agent
python -m venv nexus-env
nexus-env\Scripts\activate
pip install -r requirements.txt
# Add your Gemini, Qdrant, and NewsAPI keys to a .env file
python test_setup.py
```

---

## Project Status

🔨 Day 1 of 26 complete — environment fully set up and verified.

---

*Built by Mohana Priya — B.E ECE, Rajalakshmi Engineering College*