# app2.py  -- Robust local Ollama + FAISS RAG (Streamlit)
# Includes automatic nltk resource download and safe fallbacks to avoid the WordListCorpusReader error.
import streamlit as st
from pathlib import Path
import os
import shutil
import traceback
import inspect
import requests
import faiss
import sys

# -------------------- NLTK setup (must run before llama_index imports) --------------------
# LlamaIndex's sentence splitter uses NLTK 'punkt' and 'stopwords'. Ensure they exist,
# and provide safe fallbacks if downloads aren't possible.
try:
    import nltk
    NLTK_DATA_DIR = str(Path.home() / "nltk_data")
    # ensure nltk_data path exists and is known to nltk
    Path(NLTK_DATA_DIR).mkdir(parents=True, exist_ok=True)
    if NLTK_DATA_DIR not in nltk.data.path:
        nltk.data.path.append(NLTK_DATA_DIR)

    def _ensure_nltk_resource(resource_path, download_name):
        try:
            nltk.data.find(resource_path)
            return True
        except Exception:
            try:
                nltk.download(download_name, download_dir=NLTK_DATA_DIR, quiet=True)
                nltk.data.find(resource_path)
                return True
            except Exception:
                return False

    punkt_ok = _ensure_nltk_resource("tokenizers/punkt", "punkt")
    stopwords_ok = _ensure_nltk_resource("corpora/stopwords", "stopwords")

    if not punkt_ok or not stopwords_ok:
        # fallback: monkeypatch nltk.corpus.stopwords.words and provide simple tokenizer
        import types
        fallback_stopwords = {
            "a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at","be","because","been","before","being","below",
            "between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few",
            "for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him",
            "himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't",
            "my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same","she","she'd","she'll",
            "she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they",
            "they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've",
            "were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you",
            "you'd","you'll","you're","you've","your","yours","yourself","yourselves"
        }
        class _DummyStopwords:
            @staticmethod
            def words(lang="english"):
                return list(fallback_stopwords)

        # ensure nltk.corpus exists and set stopwords
        try:
            if not hasattr(nltk, "corpus"):
                nltk.corpus = types.SimpleNamespace()
            nltk.corpus.stopwords = _DummyStopwords
        except Exception:
            # as last resort, inject small module into sys.modules to satisfy imports
            mod_name = "nltk.corpus"
            if mod_name not in sys.modules:
                sys.modules[mod_name] = types.SimpleNamespace(stopwords=_DummyStopwords)
        # provide a simple sentence splitter used as a fallback by LlamaIndex if punkt missing
        # LlamaIndex imports nltk.tokenize.punkt internally; we can't easily replace it, but ensuring
        # stopwords avoids the specific AttributeError. We'll also set a global flag to inform user.
        NLTK_FALLBACK = True
    else:
        NLTK_FALLBACK = False

except Exception as e:
    # NLTK itself missing or failing - provide minimal fallback
    NLTK_FALLBACK = True
    class _DummyStopwords:
        @staticmethod
        def words(lang="english"):
            return []
    import types, sys
    sys.modules.setdefault("nltk", types.SimpleNamespace(corpus=types.SimpleNamespace(stopwords=_DummyStopwords)))
    # Not ideal, but avoids the attribute error inside LlamaIndex

# -------------------- Now import LlamaIndex and Ollama-related adapters --------------------
from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
# Ollama adapter import
try:
    from llama_index.llms.ollama import Ollama
except Exception:
    Ollama = None

from llama_index.vector_stores.faiss import FaissVectorStore

# -------------------- Streamlit UI config --------------------
st.set_page_config(page_title="Windows Local RAG", layout="wide", page_icon="🪟")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = str(BASE_DIR / "data")
STORAGE_DIR = str(BASE_DIR / "storage")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)


OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama HTTP endpoint

# -------------------- Helper: query Ollama for installed models --------------------
def ollama_list_models(base_url=OLLAMA_BASE_URL, timeout=3.0):
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        models = []
        if isinstance(data, dict):
            if "models" in data and isinstance(data["models"], list):
                for m in data["models"]:
                    if isinstance(m, dict):
                        name = m.get("name") or m.get("model") or m.get("id")
                        if name:
                            models.append(name)
                    elif isinstance(m, str):
                        models.append(m)
            else:
                if "name" in data:
                    models.append(data["name"])
        elif isinstance(data, list):
            for m in data:
                if isinstance(m, dict):
                    name = m.get("name") or m.get("model") or m.get("id")
                    if name:
                        models.append(name)
        return models
    except Exception:
        return []

installed_models = ollama_list_models()

# -------------------- Sidebar / System Config --------------------
with st.sidebar:
    st.header("⚙️ System Config")
    st.info("Running locally on Windows (Ollama preferred)")

    if installed_models:
        model_name = st.selectbox("Select LLM Model", installed_models, index=0)
    else:
       model_name = st.selectbox("Select LLM Model", ["llama3.2:1b", "llama3.1", "llama3", "tinyllama"], index=0)


    st.divider()
    chunk_size = st.slider("Chunk Size", 256, 1024, 512, help="Smaller chunks often give more precise answers.")
    k_similarity = st.slider("Documents to Retrieve", 1, 10, 3, help="More docs = more context but slower.")
    if NLTK_FALLBACK:
        st.warning("NLTK resources (punkt/stopwords) not fully available — using safe fallbacks. Sentence splitting may be less precise.")
    st.warning("Ensure Ollama daemon is running and 'nomic-embed-text' is pulled if using Ollama embeddings.")

# -------------------- Robust init_settings --------------------
@st.cache_resource
def init_settings(llm_model_name, chunk_size, hf_embedding_choice=None):
    try:
        if Ollama is None:
            raise RuntimeError("Ollama LLM adapter not found. Install the adapter package: pip install llama-index-llms-ollama")

        llm = Ollama(
            model=llm_model_name,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
            request_timeout=360,
        )

        embed_model = None
        embed_source = None
        try:
            from llama_index.embeddings.ollama import OllamaEmbedding
            sig = inspect.signature(OllamaEmbedding.__init__)
            params = sig.parameters
            if "model_name" in params:
                embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url=OLLAMA_BASE_URL)
            elif "model" in params:
                embed_model = OllamaEmbedding(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
            else:
                embed_model = OllamaEmbedding("nomic-embed-text", base_url=OLLAMA_BASE_URL)
            embed_source = "ollama"
        except Exception as oll_exc:
            hf_errors = []
            hf_wrapper = None
            hf_choices = [
                ("llama_index.embeddings.huggingface", "HuggingFaceEmbeddings"),
                ("llama_index.embeddings", "HuggingFaceEmbeddings"),
                ("llama_index.embeddings.huggingface", "HuggingFaceEmbedding"),
                ("llama_index.embeddings", "HuggingFaceEmbedding"),
            ]
            for module_path, class_name in hf_choices:
                try:
                    mod = __import__(module_path, fromlist=[class_name])
                    cls = getattr(mod, class_name)
                    sig = inspect.signature(cls.__init__)
                    params = sig.parameters
                    model_arg = "model_name" if "model_name" in params else ("model" if "model" in params else None)
                    hf_model = hf_embedding_choice or "sentence-transformers/all-MiniLM-L6-v2"
                    if model_arg == "model_name":
                        hf_wrapper = cls(model_name=hf_model)
                    elif model_arg == "model":
                        hf_wrapper = cls(model=hf_model)
                    else:
                        hf_wrapper = cls(hf_model)
                    embed_model = hf_wrapper
                    embed_source = "huggingface"
                    break
                except Exception as e:
                    hf_errors.append(f"{module_path}.{class_name}: {e}")

            if embed_model is None:
                combined_msg = (
                    "No embedding backend available. Tried OllamaEmbedding and multiple HuggingFace wrappers.\n\n"
                    f"OllamaEmbedding attempt error: {oll_exc}\n\n"
                    "HuggingFace attempts:\n" + "\n".join(hf_errors)
                )
                raise RuntimeError(combined_msg)

        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = chunk_size

        return {"ok": True, "embed_source": embed_source}
    except Exception as e:
        st.error("Error initializing models: " + str(e))
        st.error(traceback.format_exc())
        return {"ok": False, "error": str(e)}

init_result = init_settings(model_name, chunk_size)
if not init_result.get("ok"):
    st.sidebar.error("Model init failed. See main area for details.")
    st.stop()
else:
    st.sidebar.success(f"Loaded {model_name} (embeddings: {init_result.get('embed_source')})")

# -------------------- Embedding detection & FAISS helpers --------------------
def _get_embed_dim_or_raise():
    embed_model = Settings.embed_model
    if embed_model is None:
        raise RuntimeError("Settings.embed_model is not configured")

    sample = "hello world"
    emb = None
    if hasattr(embed_model, "get_text_embedding"):
        emb = embed_model.get_text_embedding(sample)
    elif hasattr(embed_model, "embed"):
        out = embed_model.embed([sample])
        if isinstance(out, list) and len(out) > 0:
            emb = out[0]
        else:
            emb = out
    else:
        try:
            emb = embed_model(sample)
        except Exception as e:
            raise RuntimeError("Unable to call embedding model to infer dimension: " + str(e))

    if emb is None:
        raise RuntimeError("Embedding model returned None for sample text")
    try:
        dim = len(emb)
    except Exception as e:
        raise RuntimeError("Unable to determine embedding vector length: " + str(e))
    return int(dim)

def safe_remove_storage():
    try:
        if os.path.exists(STORAGE_DIR):
            shutil.rmtree(STORAGE_DIR)
            Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        st.error(f"Failed to remove storage dir: {e}")

# -------------------- Index loader / builder --------------------
def load_or_build_index(rebuild=False):
    try:
        EMBED_DIM = _get_embed_dim_or_raise()
    except Exception as e:
        st.error(f"Embedding dimension detection failed: {e}")
        st.error(traceback.format_exc())
        return None

    faiss_index = faiss.IndexFlatL2(EMBED_DIM)
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    if rebuild:
        safe_remove_storage()

    if os.path.exists(STORAGE_DIR) and os.listdir(STORAGE_DIR) and not rebuild:
        try:
            storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR, vector_store=vector_store)
            index = load_index_from_storage(storage_context)
            return index
        except AssertionError:
            st.warning("Detected FAISS embedding-dimension mismatch. Rebuilding storage...")
            safe_remove_storage()
        except Exception as e:
            st.warning(f"Index load failed; will rebuild. Error: {e}")
            st.error(traceback.format_exc())

    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    
    documents = SimpleDirectoryReader(DATA_DIR).load_data()

    if not documents:
        st.warning("No documents found. Add files to the data directory.")
        return None

    if rebuild:
        safe_remove_storage()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )
    with st.spinner(f"Processing {len(documents)} documents..."):
            st.write("Creating embeddings and building index...")
            

            index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context
    )

        
            index.storage_context.persist(persist_dir=STORAGE_DIR)

    return index


# -------------------- UI --------------------
st.title("🧠 Windows Knowledge Base (Local RAG)")
st.markdown(f"Chat with your documents using **{model_name}** locally via Ollama.")
if NLTK_FALLBACK:
    st.warning("NLTK data not fully available; using safe fallbacks for tokenization/stopwords.")

tab1, tab2 = st.tabs(["💬 Chat Interface", "📂 File Manager"])

with tab2:
    st.subheader("Manage Documents")
    uploaded_files = st.file_uploader("Drop PDF, TXT, or MD files here", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = Path(DATA_DIR) / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} files to {DATA_DIR}")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚨 Rebuild Knowledge Base", type="primary"):
            st.session_state.index = load_or_build_index(rebuild=True)
            st.rerun()
    with col2:
        if os.path.exists(DATA_DIR):
            files = os.listdir(DATA_DIR)
            st.caption(f"Files: {', '.join(files)}")

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload documents in the File Manager tab to begin."}]

    if "index" not in st.session_state:
        idx = load_or_build_index(rebuild=False)
        if idx:
            st.session_state.index = idx
        else:
            st.info("⚠️ No index available. Upload documents in File Manager to build the knowledge base.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if "index" in st.session_state and st.session_state.index:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                try:
                    query_engine = st.session_state.index.as_query_engine(similarity_top_k=k_similarity, streaming=True)
                    response = query_engine.query(prompt)
                    output = ""
                    streamed = False
                    if hasattr(response, "response_gen"):
                        gen = getattr(response, "response_gen")
                        try:
                            for token in gen:
                                streamed = True
                                output += token
                                placeholder.markdown(output + "▌")
                        except Exception:
                            streamed = False
                    if not streamed:
                        if hasattr(response, "response") and response.response:
                            output = response.response
                        elif hasattr(response, "get_formatted_reply"):
                            try:
                                output = response.get_formatted_reply()
                            except Exception:
                                output = str(response)
                        elif hasattr(response, "output") and response.output:
                            output = response.output
                        else:
                            output = str(response)
                        if not output or output.strip() == "":
                            placeholder.markdown("**Empty Response**")
                            with st.expander("Debug: response object info", expanded=False):
                                st.write("type:", type(response))
                                attrs = [a for a in dir(response) if not a.startswith("_")]
                                st.write("attrs (sample):", attrs[:80])
                                for attr in ("response", "response_gen", "get_formatted_reply", "output"):
                                    if hasattr(response, attr):
                                        try:
                                            val = getattr(response, attr)
                                            st.write(f"{attr}:", (val if isinstance(val, (str, int, float)) else type(val)))
                                        except Exception as e:
                                            st.write(f"{attr}: <error reading: {e}>")
                        else:
                            placeholder.markdown(output)
                    else:
                        placeholder.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    st.error(traceback.format_exc())
        else:
            st.error("Index not ready. Please build the knowledge base in File Manager (and check logs).")
