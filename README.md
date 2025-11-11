### 3. Kiến trúc hệ thống (System Architecture)

Hệ thống được xây dựng dựa trên kiến trúc Retrieval-Augmented Generation (RAG) bao gồm các thành phần chính sau:

1.  **Giao diện người dùng (User Interface):**
    *   Xây dựng bằng **Streamlit** (`app.py`).
    *   Tiếp nhận câu hỏi từ người dùng và hiển thị câu trả lời do AI tạo ra.

2.  **Thành phần RAG lõi (Core RAG Component):**
    *   `legal_rag.py`: Class `LegalRAGSystem` điều phối toàn bộ luồng xử lý.
    *   **LLM Provider**: Hỗ trợ linh hoạt giữa các nhà cung cấp LLM như **Google Gemini** và các mô hình local qua **Ollama**. Cấu hình qua biến môi trường `LLM_PROVIDER`.
    *   **Embedding Provider**: Hỗ trợ **HuggingFace Embeddings** (mặc định) và **Google Generative AI Embeddings**.

3.  **Truy xuất thông tin (Retriever):**
    *   **Vector Store**: Sử dụng **FAISS** để lưu trữ và truy vấn các vector tài liệu một cách hiệu quả. Cơ sở dữ liệu vector được lưu tại `vectorstore/`.
    *   **Retriever**: Thực hiện tìm kiếm tương đồng (similarity search) để lấy ra các đoạn văn bản có liên quan nhất từ Vector Store.

4.  **Xử lý dữ liệu (Data Processing):**
    *   `document_processor.py`: Chứa logic để đọc các loại tài liệu khác nhau (`.pdf`, `.docx`, `.txt`) từ thư mục `data/`.
    *   **Text Splitter**: Sử dụng `RecursiveCharacterTextSplitter` của LangChain để chia nhỏ tài liệu thành các đoạn (chunks) có kích thước phù hợp.
    *   `rebuild_kb.py`: Script để kích hoạt quá trình xử lý tài liệu và xây dựng lại cơ sở dữ liệu FAISS từ đầu.

### 4. Cài đặt (Setup and Installation)

Để chạy dự án trên máy cục bộ, hãy làm theo các bước sau:

1.  **Clone a repository:**
    ```bash
    git clone <your-repository-url>
    cd law_chatbot
    ```

2.  **Tạo môi trường ảo và cài đặt thư viện:**
    ```bash
    # Tạo môi trường ảo
    python -m venv venv

    # Kích hoạt môi trường (trên Windows)
    .\venv\Scripts\activate

    # Kích hoạt môi trường (trên macOS/Linux)
    source venv/bin/activate

    # Cài đặt các thư viện cần thiết
    pip install -r requirements.txt
    ```

3.  **Cấu hình biến môi trường:**
    *   Tạo một file tên là `.env` bằng cách sao chép từ file `env.example`.
    *   Điền các giá trị cần thiết, đặc biệt là `GOOGLE_API_KEY`.
    ```
    # .env
    LLM_PROVIDER=google
    EMBEDDING_PROVIDER=huggingface

    # Google Gemini
    GOOGLE_API_KEY="your_google_api_key"
    GOOGLE_CHAT_MODEL=gemini-1.5-flash

    # Ollama (nếu sử dụng)
    OLLAMA_MODEL=llama3
    OLLAMA_BASE_URL=http://localhost:11434
    ```

### 5. Hướng dẫn sử dụng (Usage)

#### 5.1. Nạp dữ liệu và xây dựng Knowledge Base

Trước khi chạy ứng dụng, bạn cần chuẩn bị cơ sở dữ liệu vector.

1.  Đặt các tài liệu pháp lý của bạn (file `.pdf`, `.docx`, `.txt`) vào thư mục `data/`.
2.  Chạy script sau để xử lý tài liệu và tạo FAISS index:
    ```bash
    python rebuild_kb.py
    ```
    Quá trình này sẽ tạo ra thư mục `vectorstore/legal_faiss` chứa index.

#### 5.2. Chạy ứng dụng Chatbot

Sử dụng Streamlit để khởi chạy giao diện web:
```bash
streamlit run app.py
```
Mở trình duyệt và truy cập vào địa chỉ `http://localhost:8501`.

### 6. Đánh giá chất lượng (Evaluation)

Dự án đi kèm một notebook (`evaluate.ipynb`) để đánh giá chất lượng của hệ thống RAG bằng bộ dữ liệu `ViBidLQA` và thư viện `RAGAs`.

1.  Mở và chạy các cell trong notebook `evaluate.ipynb`.
2.  Notebook sẽ tự động:
    *   Tải bộ dữ liệu.
    *   Tạo câu trả lời từ hệ thống RAG cho các câu hỏi trong bộ dữ liệu.
    *   Tính toán các chỉ số: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`.
    *   Hiển thị bảng điểm kết quả.

Đây là một bước quan trọng để đo lường và chứng minh hiệu quả của mô hình.

### 7. Lộ trình phát triển (Future Roadmap)

-   [ ] **Tối ưu hóa RAG**:
    -   [ ] Tích hợp kỹ thuật Reranking (sử dụng Cross-encoders) để cải thiện độ chính xác của context.
    -   [ ] Thử nghiệm các phương pháp Query Transformation (như Multi-Query) để xử lý các câu hỏi phức tạp.
-   [ ] **MLOps**:
    -   [ ] Đóng gói ứng dụng với `Dockerfile`.
    -   [ ] Thiết lập CI/CD pipeline với GitHub Actions để tự động chạy test.
    -   [ ] Triển khai ứng dụng lên một nền tảng đám mây (ví dụ: Azure App Service, Google Cloud Run).
-   [ ] **Cải thiện UX**:
    -   [ ] Hiển thị nguồn (document citation) cho mỗi câu trả lời.
    -   [ ] Thêm cơ chế thu thập phản hồi của người dùng (feedback).
    -   [ ] Hỗ trợ lịch sử hội thoại.
