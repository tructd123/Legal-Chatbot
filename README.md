# Legal RAG Chatbot for Vietnamese Law

This project implements a sophisticated Retrieval-Augmented Generation (RAG) chatbot specialized in answering questions about Vietnamese law. It leverages state-of-the-art language models and a robust document processing pipeline, including an advanced OCR fallback mechanism, to provide accurate, context-aware answers from a custom knowledge base of legal documents.

## Key Features

- **Hybrid Document Processing**: Ingests various document formats (`.pdf`, `.docx`, `.txt`).
- **Advanced OCR Fallback**: Utilizes a multi-layered approach for text extraction from PDFs. It first tries fast and accurate methods (PyMuPDF, pdfplumber) and automatically falls back to a Tesseract-based OCR pipeline for scanned or image-based documents.
- **Configurable OCR**: Fine-tune OCR performance via environment variables for language, DPI, and Tesseract's Page Segmentation Mode (PSM).
- **Flexible LLM & Embedding Support**: Easily switch between different providers:
    - **LLMs**: Google Gemini, Ollama.
    - **Embeddings**: Google (`models/embedding-001`), HuggingFace (`sentence-transformers`).
- **Efficient Vector Storage**: Uses FAISS for creating and querying a local vector database, ensuring fast retrieval.
- **Streamlit UI**: A simple and interactive web interface for asking questions and viewing answers with their sources.
- **RAGAs Evaluation**: Includes a Jupyter notebook (`evaluate.ipynb`) to quantitatively assess the RAG system's performance on metrics like `faithfulness`, `answer_relevancy`, `context_precision`, and `context_recall`.

## Technology Stack

- **Core Framework**: LangChain
- **LLM**: Google Gemini (default), Ollama
- **Embeddings**: Google Embeddings, Sentence-Transformers
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **UI**: Streamlit
- **Document Processing**: PyMuPDF, pdfplumber, python-docx
- **OCR**: Tesseract, pdf2image, Poppler
- **Evaluation**: RAGAs, Datasets (Hugging Face)

---

## Setup and Installation

### 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10+**
- **Poppler**: Required by `pdf2image` to convert PDFs to images for OCR.
    - **Windows**: Download the latest binary from the [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) page. Unzip it to a location like `C:\Program Files\poppler-24.02.0` and add the `\bin` subdirectory to your system's PATH.
    - **macOS**: `brew install poppler`
    - **Linux**: `sudo apt-get install poppler-utils`
- **Tesseract OCR Engine**: Required for OCR on scanned documents.
    - **Windows**: Download and run the installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Make sure to install the Vietnamese language pack (`vie`). Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's PATH.
    - **macOS**: `brew install tesseract`
    - **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-vie`

### 2. Clone the Repository

```bash
git clone https://github.com/tructd123/Legal-Chatbot.git
cd Legal-Chatbot
```

### 3. Set Up a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env` in the root of the project directory by copying the example:

```bash
# On Windows
copy .env.example .env
# On macOS/Linux
cp .env.example .env
```

Now, edit the `.env` file with your credentials and desired configurations:

```dotenv
# --- API Keys & Provider Configuration ---
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
LLM_PROVIDER="google" # Or "ollama"
EMBEDDING_PROVIDER="google" # Or "huggingface"

# --- Model Configuration ---
GOOGLE_CHAT_MODEL="gemini-1.5-flash"
GOOGLE_EMBEDDING_MODEL="models/embedding-001"
OLLAMA_MODEL="llama3.1" # If using Ollama
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" # If using HuggingFace

# --- OCR Engine Paths (IMPORTANT for Windows) ---
# Full path to the Poppler 'bin' directory
POPPLER_PATH="C:/path/to/poppler-xx.xx.x/Library/bin"
# Full path to the Tesseract executable
TESSERACT_CMD="C:/Program Files/Tesseract-OCR/tesseract.exe"

# --- OCR Performance Tuning ---
PDF_OCR_LANG="vie"          # Language for Tesseract (e.g., 'vie' for Vietnamese)
PDF_OCR_DPI=300             # DPI for rendering PDF pages to images. Higher values are clearer but slower.
PDF_OCR_CONFIG="--oem 1 --psm 4" # Tesseract config. psm 4 (auto page segmentation) is good for multi-column docs.
PDF_OCR_VERBOSE="0"         # Set to "1" to see character counts for each OCR'd page.
```

---

## Usage

### 1. Add Legal Documents

Place your legal documents (`.pdf`, `.docx`, `.txt`) into the `data/` directory.

### 2. Build the Knowledge Base

Run the following script to process the documents in the `data/` folder, generate embeddings, and create the FAISS vector store. This only needs to be done once, or whenever you add/update documents.

```bash
python rebuild_kb.py
```

This will create a `vectorstore/legal_faiss` directory containing the indexed knowledge base.

### 3. Run the Chatbot

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Open your web browser to the local URL provided by Streamlit (usually `http://localhost:8501`) to start interacting with the chatbot.

### 4. Evaluate the System (Optional)

The `evaluate.ipynb` notebook allows you to assess the performance of the RAG pipeline using the RAGAs framework.

1.  **Download Data**: The notebook is configured to use the `ViBidLQA` dataset. You may need to run the initial cells to download it from Hugging Face.
2.  **Generate Answers**: The notebook will take a sample of questions, generate answers using your RAG system, and retrieve the contexts used.
3.  **Evaluate**: It then computes scores for `faithfulness`, `answer_relevancy`, `context_precision`, and `context_recall`.

To run it, start a Jupyter server in your activated virtual environment:

```bash
jupyter notebook
```

Then, open `evaluate.ipynb` and run the cells sequentially.
