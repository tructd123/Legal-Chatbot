import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from document_processor import LegalDocumentProcessor
import traceback

# Load environment variables
load_dotenv()

class LegalRAGSystem:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "huggingface").lower()
        if embedding_provider == "google" and self.google_api_key:
            embedding_model = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
            print(f"🔄 Using Google embeddings model: {embedding_model}")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=embedding_model,
                google_api_key=self.google_api_key
            )
        else:
            embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            print(f"🔄 Using HuggingFace embeddings model: {embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

        llm_provider = os.getenv("LLM_PROVIDER", "google").lower()
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

        if llm_provider == "google":
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY is required when LLM_PROVIDER=google.")
            chat_model = os.getenv("GOOGLE_CHAT_MODEL", "gemini-1.5-flash-8b")
            print(f"🔄 Using Google chat model: {chat_model}")
            self.llm = ChatGoogleGenerativeAI(
                model=chat_model,
                temperature=temperature,
                google_api_key=self.google_api_key
            )
        elif llm_provider == "ollama":
            chat_model = os.getenv("OLLAMA_MODEL", "llama3.1")
            print(f"🔄 Using Ollama chat model: {chat_model}")
            self.llm = ChatOllama(
                model=chat_model,
                temperature=temperature
            )
        else:
            raise ValueError("Unsupported LLM_PROVIDER. Use 'google' or 'ollama'.")

        self.vector_store = None

        # Prompt template
        self.legal_prompt = PromptTemplate(
            template="""Bạn là một trợ lý AI chuyên về pháp luật Việt Nam. 
Hãy trả lời câu hỏi dựa trên các văn bản pháp luật được cung cấp.

NGUYÊN TẮC:
1. Chỉ trả lời dựa trên thông tin có trong văn bản pháp luật được cung cấp
2. Nếu không có thông tin đủ, hãy nói "Tôi không tìm thấy thông tin này trong các văn bản pháp luật hiện có"
3. Trích dẫn cụ thể điều, khoản liên quan nếu có
4. Sử dụng ngôn ngữ pháp luật chính xác và dễ hiểu
5. Đưa ra lời khuyên thận trọng, khuyến khích tham khảo luật sư nếu cần

Văn bản pháp luật tham khảo:
{context}

Câu hỏi: {question}

Trả lời:""",
            input_variables=["context", "question"]
        )

    def build_knowledge_base(self, data_folder: str = "data"):
        print("🔄 Đang xử lý tài liệu pháp luật...")
        if not os.path.exists(data_folder):
            raise ValueError(f"Thư mục {data_folder} không tồn tại!")
        files = os.listdir(data_folder)
        if not files:
            raise ValueError(f"Không có file nào trong thư mục {data_folder}!")
        print(f"📁 Tìm thấy {len(files)} file trong thư mục data: {files}")

        try:
            processor = LegalDocumentProcessor()
            documents = processor.process_documents(data_folder)
            if not documents:
                raise ValueError("Không thể xử lý tài liệu nào!")
            print(f"📚 Đã xử lý {len(documents)} chunks từ tài liệu pháp luật")

            # Tạo vector store
            print("🔄 Đang tạo vector database...")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            os.makedirs("vectorstore", exist_ok=True)
            print("💾 Đang lưu vector database...")
            self.vector_store.save_local("vectorstore/legal_faiss")
            print("✅ Knowledge base đã được xây dựng thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi xây dựng knowledge base: {e}")
            traceback.print_exc()
            raise e

    def load_knowledge_base(self):
        vectorstore_path = "vectorstore/legal_faiss"
        if not os.path.exists(vectorstore_path):
            print("❌ Không tìm thấy vectorstore. Cần xây dựng knowledge base.")
            return False
        try:
            required_files = ["index.faiss", "index.pkl"]
            for file in required_files:
                if not os.path.exists(os.path.join(vectorstore_path, file)):
                    print(f"❌ Thiếu file: {file}")
                    return False
            print("🔄 Đang load vectorstore...")
            self.vector_store = FAISS.load_local(
                vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("✅ Đã load knowledge base thành công!")
            return True
        except Exception as e:
            print(f"❌ Không thể load knowledge base: {e}")
            traceback.print_exc()
            return False

    def query(self, question: str) -> dict:
        if not self.vector_store:
            return {"answer": "Hệ thống chưa được khởi tạo. Vui lòng xây dựng knowledge base trước.", "sources": []}
        try:
            retrieved_docs = self.vector_store.similarity_search(question, k=5)
            if not retrieved_docs:
                return {
                    "answer": "Tôi không tìm thấy thông tin này trong các văn bản pháp luật hiện có.",
                    "sources": []
                }

            context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
            prompt = self.legal_prompt.format(context=context_text, question=question)
            response = self.llm.invoke(prompt)

            if hasattr(response, "content"):
                answer_text = response.content
            else:
                answer_text = str(response)

            if not answer_text or answer_text.strip() == "":
                answer_text = "Tôi không tìm thấy thông tin này trong các văn bản pháp luật hiện có."

            sources = []
            for i, doc in enumerate(retrieved_docs):
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_index", i),
                    "page": doc.metadata.get("page_number", "N/A")
                })

            return {"answer": answer_text, "sources": sources}
        except Exception as e:
            print(f"❌ Lỗi khi xử lý câu hỏi: {e}")
            traceback.print_exc()
            return {"answer": f"Có lỗi xảy ra khi xử lý câu hỏi: {e}", "sources": []}

    def debug_chain_inputs(self, question: str, k: int = 5) -> dict:
        if not self.vector_store:
            raise RuntimeError("Knowledge base chưa sẵn sàng. Vui lòng xây dựng hoặc load trước.")

        retrieved_docs = self.vector_store.similarity_search(question, k=k)
        context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt = self.legal_prompt.format(context=context_text, question=question)

        debug_docs = []
        for i, doc in enumerate(retrieved_docs):
            debug_docs.append({
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_index": doc.metadata.get("chunk_index", i),
                "page_number": doc.metadata.get("page_number", "N/A")
            })

        return {
            "question": question,
            "retrieved_documents": debug_docs,
            "prompt": prompt
        }

    def get_related_articles(self, query: str, k: int = 3) -> List[dict]:
        if not self.vector_store:
            return []
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "similarity_score": "High",
                    "page": doc.metadata.get("page_number", "N/A")
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"Lỗi khi tìm điều luật liên quan: {e}")
            return []


if __name__ == "__main__":
    rag = LegalRAGSystem()
    if not rag.load_knowledge_base():
        rag.build_knowledge_base("data")
    question = "Quy định về thời hạn sử dụng đất nông nghiệp là gì?"
    answer = rag.query(question)
    print("\n=== CÂU TRẢ LỜI ===")
    print(answer["answer"])
    print("\n=== NGUỒN ===")
    for src in answer["sources"]:
        print(f"- {src['source']} (chunk {src['chunk_id']}, page {src['page']})")
