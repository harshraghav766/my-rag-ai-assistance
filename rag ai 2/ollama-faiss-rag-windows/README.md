# 🧠 RAG AI Teaching Assistant

### An AI-powered teaching assistant that answers questions using your uploaded study materials.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-Web%20App-red?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-orange?style=for-the-badge" />
</p>

---

## 📌 About the Project

**RAG AI Teaching Assistant** is a document-based AI application built using Python and Retrieval-Augmented Generation (RAG).

The application allows users to upload study materials and ask questions based on the available documents. It retrieves relevant information from the knowledge base and uses a language model to generate helpful answers.

The project combines document retrieval, vector search, embeddings, and a local Large Language Model (LLM) to create an interactive learning experience.

## ✨ Key Features

- 📚 **Document-Based Question Answering** — Ask questions about your study materials.
- 🧠 **Retrieval-Augmented Generation (RAG)** — Retrieve relevant document content before generating answers.
- 🔎 **Semantic Search** — Find relevant information using vector embeddings and FAISS.
- 💬 **Interactive Chat Interface** — Ask questions through a Streamlit web application.
- 📁 **Document Management** — Upload and manage supported study documents.
- 🤖 **Local AI Inference** — Use Ollama to run supported language models locally.
- 🔐 **Privacy-Focused Design** — Documents and model inference can remain on your own machine when using the local setup.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| Ollama | Running local language models |
| FAISS | Vector similarity search |
| Embeddings | Representing document content numerically |
| RAG | Retrieving context to answer questions |

## ⚙️ How It Works

1. **Upload Documents:** Add your study materials to the application.
2. **Process Documents:** Extract and prepare document content.
3. **Generate Embeddings:** Convert text into vector representations.
4. **Build Knowledge Base:** Store vectors in a FAISS index.
5. **Ask Questions:** Enter a question in the chat interface.
6. **Retrieve Context:** Find relevant document content.
7. **Generate Answer:** Send the retrieved context to the language model to generate a response.

## 🚀 Getting Started

### 1. Prerequisites

Install the following:

- Python 3.10 or a compatible version
- Git
- Ollama for local model inference

Download Ollama: https://ollama.com/download

### 2. Clone the Repository

```bash
git clone https://github.com/harshraghav766/my-rag-ai-assistance.git
cd my-rag-ai-assistance
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Download the Required Models

The current local setup uses these Ollama models:

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

Make sure Ollama is installed and running.

### 5. Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

> **Note:** The commands above assume your repository contains `app.py` and `requirements.txt`, and that the application is configured to use these Ollama models.

## 📂 Project Structure

```text
my-rag-ai-assistance/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/          # Local document storage, if configured
└── storage/       # Generated vector index, if configured
```

The exact folder structure may vary depending on your implementation.

## 🎯 Project Objective

The goal of this project is to explore how Retrieval-Augmented Generation can make learning easier by allowing users to interact with their own educational content through natural-language questions.

It demonstrates practical applications of Python, NLP concepts, vector databases, LLMs, and AI-powered application development.

## 🔮 Future Improvements

- Deploy an online version for public access.
- Add support for more document formats.
- Improve retrieval accuracy and answer quality.
- Add conversation history and source references.
- Create a more advanced learning assistant interface.
- Integrate a hosted AI model for cloud deployment.

## 👨‍💻 Developer

**Harshit Kumar**

BCA Student | Aspiring Data Analyst & Data Scientist

Interested in Python, Data Science, Machine Learning, and AI-powered applications.

- **GitHub:** https://github.com/harshraghav766
- **Project Repository:** https://github.com/harshraghav766/my-rag-ai-assistance

## 📄 License

This project is intended for educational and learning purposes. Add a `LICENSE` file if you want to publish it under a specific open-source license.

---

⭐ If you find this project interesting, consider starring the repository!
