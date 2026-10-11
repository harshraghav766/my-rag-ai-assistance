# 🧠 Windows Local RAG — Streamlit + Ollama + FAISS  
*A fully local Retrieval-Augmented Generation system for Windows.*

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-Ollama-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VectorDB-FAISS-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/UI-Streamlit-red?style=for-the-badge" />
</p>

---

## 📌 Overview

**Windows Local RAG** is an offline, privacy-first document retrieval system that lets you:

- Upload PDFs, TXT, and MD files  
- Build a vector knowledge base using **FAISS**  
- Query documents with **local LLMs via Ollama**  
- Get streamed chat responses  
- Automatically handle missing NLTK corpora  
- Use HuggingFace embeddings as fallback  

Designed to run *100% locally on Windows* with no cloud dependencies.

---

## 🚀 Features

### 🔍 Retrieval-Augmented Generation
Uses FAISS + dynamic embedding backend:
- `nomic-embed-text` via Ollama  
- OR HuggingFace embeddings if Ollama embedding fails  

### 🧠 Local LLM Support
Works with any installed Ollama model:
- `llama3.1`
- `llama3`
- `tinyllama`
- `phi3`
- many more…

### 📁 Document Manager
- Drag & drop documents  
- View stored files  
- Rebuild the FAISS index anytime  

### 💬 Chat Interface
- Token streaming  
- Clean UI  
- Fully local, no API keys required  

### ⚡ Stability Enhancements
- Auto-detects embedding dimensions  
- Fixes FAISS index mismatch errors  
- Safe fallbacks for missing NLTK `punkt` & `stopwords`  

---

## 🛠️ Installation

### 1️⃣ Install Python (3.10–3.12 recommended)

### 2️⃣ Install project dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Install Ollama (Windows)
Download: https://ollama.com/download

Pull required models:
```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

---

## ▶️ Run the Application

```bash
streamlit run app2.py
```

App opens at:

```
http://localhost:8501
```

---

## 📂 Project Structure

```
windows-local-rag-ollama-faiss/
│
├── app2.py                 # Main application code
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/                   # Uploaded documents
├── storage/                # FAISS index (auto-generated)
│
└── screenshots/            # Optional images for README
```

---

## 📦 Requirements (`requirements.txt`)

```
streamlit
llama-index
llama-index-llms-ollama
faiss-cpu
requests
nltk
sentence-transformers
```

Optional:
```
pypdf
python-dotenv
```

---

## 📸 Screenshots (Optional)

Add screenshots to a folder:

```
![App Screenshot](screenshots/home.png)
```

---

## 🧰 Troubleshooting

### ❗ Ollama not detected
Start the server:
```bash
ollama serve
```

### ❗ FAISS vector dimension mismatch
Use the **Rebuild Knowledge Base** button.

### ❗ NLTK “punkt” missing
App automatically applies fallback tokenizers.

---

## 🤝 Contributing

Pull requests and feature ideas are welcome!  
UI improvements, model integrations, and optimizations are appreciated.

---

## 📝 License

MIT License © 2025

---

## ⭐ Support This Project

Give the repo a **⭐ star** if this project helps you — it motivates future development!
