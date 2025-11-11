import streamlit as st
import os
from dotenv import load_dotenv
from legal_rag import LegalRAGSystem

# Load environment variables
load_dotenv()

# Cấu hình trang
st.set_page_config(
    page_title="Chatbot Pháp Luật Việt Nam",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}

.main-header h1 {
    color: white;
    text-align: center;
    margin: 0;
}

.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #2a5298;
}

.user-message {
    background-color: #f0f2f6;
    border-left-color: #ff6b6b;
}

.bot-message {
    background-color: #e8f4f8;
    border-left-color: #2a5298;
}

.source-box {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 0.5rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_rag_system():
    """Khởi tạo RAG system"""
    if 'rag_system' not in st.session_state:
        with st.spinner("🔄 Đang khởi tạo hệ thống..."):
            try:
                # Kiểm tra API key trước
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong file .env")
                    return None

                print("🔄 Đang khởi tạo LegalRAGSystem...")
                rag_system = LegalRAGSystem()
                print("✅ LegalRAGSystem đã khởi tạo")
                
                # Thử load knowledge base đã có
                print("🔄 Đang thử load knowledge base...")
                if not rag_system.load_knowledge_base():
                    st.warning("⚠️ Không tìm thấy knowledge base. Đang xây dựng mới...")
                    
                    # Kiểm tra thư mục data
                    if not os.path.exists("data") or not os.listdir("data"):
                        st.error("❌ Không tìm thấy file dữ liệu trong thư mục 'data'")
                        return None
                    
                    # Thử xây dựng mới
                    with st.spinner("🔄 Đang xây dựng knowledge base mới (có thể mất vài phút)..."):
                        rag_system.build_knowledge_base()
                        st.success("✅ Knowledge base đã được xây dựng thành công!")
                else:
                    st.success("✅ Đã load knowledge base thành công!")
                
                st.session_state.rag_system = rag_system
                return rag_system
                
            except Exception as e:
                st.error(f"❌ Lỗi khởi tạo hệ thống: {str(e)}")
                st.error("Vui lòng kiểm tra:")
                st.error("1. API key Google AI đã được cấu hình đúng")
                st.error("2. Các thư viện đã được cài đặt đầy đủ")
                st.error("3. File dữ liệu có tồn tại trong thư mục 'data'")
                
                # Hiển thị chi tiết lỗi nếu ở chế độ debug
                if st.checkbox("Hiển thị chi tiết lỗi"):
                    import traceback
                    st.code(traceback.format_exc())
                
                return None
    
    return st.session_state.rag_system

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Chatbot Pháp Luật Việt Nam</h1>
        <p style="color: white; text-align: center; margin: 0;">
            Trợ lý AI hỗ trợ tra cứu và tư vấn pháp luật
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔧 Cài đặt")
        
        # API Key check
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ API Key đã được cấu hình")
        else:
            st.error("❌ Chưa cấu hình API Key")
            st.info("Vui lòng thêm GOOGLE_API_KEY vào file .env")
        
        st.markdown("---")
        
        # Quản lý knowledge base
        st.subheader("📚 Quản lý Knowledge Base")
        
        # Hiển thị thông tin về các file trong data
        if st.button("📋 Kiểm tra dữ liệu", type="secondary"):
            data_folder = "data"
            if os.path.exists(data_folder):
                files = os.listdir(data_folder)
                if files:
                    st.success(f"Tìm thấy {len(files)} file:")
                    for file in files:
                        file_path = os.path.join(data_folder, file)
                        file_size = os.path.getsize(file_path) / 1024  # KB
                        st.info(f"📄 {file} ({file_size:.1f} KB)")
                else:
                    st.warning("Thư mục data trống")
            else:
                st.error("Không tìm thấy thư mục data")
        
        if st.button("🔄 Xây dựng lại Knowledge Base", type="primary"):
            if 'rag_system' in st.session_state:
                with st.spinner("Đang xóa knowledge base cũ và xây dựng mới..."):
                    try:
                        # Xóa vectorstore cũ
                        import shutil
                        if os.path.exists("vectorstore"):
                            shutil.rmtree("vectorstore")
                            st.info("✅ Đã xóa knowledge base cũ")
                        
                        # Xây dựng mới
                        st.session_state.rag_system.build_knowledge_base()
                        st.success("✅ Knowledge base đã được xây dựng lại thành công!")
                        
                        # Test với câu hỏi đơn giản
                        test_result = st.session_state.rag_system.query("Văn bản này quy định về vấn đề gì?")
                        if test_result["answer"] and "không tìm thấy" not in test_result["answer"].lower():
                            st.success("✅ Hệ thống hoạt động bình thường!")
                        else:
                            st.warning("⚠️ Có thể có vấn đề với dữ liệu")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
            else:
                st.error("Hệ thống chưa được khởi tạo")
        st.markdown("---")
        
        # Debug information
        st.subheader("🔍 Thông tin Debug")
        
        if st.button("📊 Kiểm tra Knowledge Base", type="secondary"):
            if 'rag_system' in st.session_state and st.session_state.rag_system.vector_store:
                try:
                    # Thử search để kiểm tra
                    test_docs = st.session_state.rag_system.vector_store.similarity_search("nghị định", k=3)
                    st.success(f"✅ Vector store hoạt động. Tìm thấy {len(test_docs)} document chunks.")
                    
                    for i, doc in enumerate(test_docs):
                        with st.expander(f"Document chunk {i+1}"):
                            st.write(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                            st.write(f"**Chunk index:** {doc.metadata.get('chunk_index', 'Unknown')}")
                            st.write(f"**Content length:** {len(doc.page_content)}")
                            st.write(f"**Content preview:** {doc.page_content[:300]}...")
                            
                except Exception as e:
                    st.error(f"❌ Lỗi kiểm tra vector store: {e}")
            else:
                st.warning("Knowledge base chưa được tải hoặc trống")
        
        st.markdown("---")
        
        # Thông tin hệ thống
        st.subheader("ℹ️ Thông tin")
        st.info("""
        **Lưu ý quan trọng:**
        - Thông tin chỉ mang tính chất tham khảo
        - Không thay thế tư vấn pháp lý chuyên nghiệp
        - Khuyến khích tham khảo luật sư khi cần thiết
        """)

    # Khởi tạo RAG system
    rag_system = initialize_rag_system()
    
    if not rag_system:
        st.error("Không thể khởi tạo hệ thống. Vui lòng kiểm tra cấu hình.")
        return

    # Chat interface
    st.subheader("💬 Hỏi đáp pháp luật")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Xin chào! Tôi là trợ lý AI chuyên về pháp luật Việt Nam. Bạn có thể hỏi tôi về các vấn đề pháp luật."
        })

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Hiển thị nguồn tham khảo nếu có
            if "sources" in message and message["sources"]:
                with st.expander("📚 Nguồn tham khảo"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>Nguồn {i+1}:</strong> {source['source']}<br>
                            <small>{source['content']}</small>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi pháp luật của bạn..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Đang tìm kiếm thông tin..."):
                response = rag_system.query(prompt)
                
                st.markdown(response["answer"])
                
                # Hiển thị nguồn tham khảo
                if response["sources"]:
                    with st.expander("📚 Nguồn tham khảo"):
                        for i, source in enumerate(response["sources"]):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Nguồn {i+1}:</strong> {source['source']}<br>
                                <small>{source['content']}</small>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"]
        })

    # Suggested questions
    st.markdown("---")
    st.subheader("💡 Câu hỏi gợi ý")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Thủ tục ly hôn", key="divorce"):
            st.session_state.suggested_question = "Thủ tục ly hôn theo pháp luật Việt Nam như thế nào?"
    
    with col2:
        if st.button("Quyền lợi người lao động", key="labor"):
            st.session_state.suggested_question = "Quyền lợi cơ bản của người lao động là gì?"
    
    with col3:
        if st.button("Hợp đồng mua bán", key="contract"):
            st.session_state.suggested_question = "Điều kiện để hợp đồng mua bán có hiệu lực?"

    # Handle suggested questions
    if hasattr(st.session_state, 'suggested_question'):
        question = st.session_state.suggested_question
        del st.session_state.suggested_question
        
        # Add to chat
        st.session_state.messages.append({"role": "user", "content": question})
        
        with st.spinner("Đang tìm kiếm thông tin..."):
            response = rag_system.query(question)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            })
        
        st.rerun()

if __name__ == "__main__":
    main()