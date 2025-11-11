#!/usr/bin/env python3
"""
Script để rebuild knowledge base nhanh chóng
"""

import os
import shutil
from dotenv import load_dotenv
from legal_rag import LegalRAGSystem

def rebuild_knowledge_base():
    """Xây dựng lại knowledge base từ đầu"""
    print("🔄 Bắt đầu rebuild knowledge base...")
    
    # Load environment variables
    load_dotenv()
    
    # Kiểm tra API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Không tìm thấy GOOGLE_API_KEY")
        return False
    
    # Kiểm tra thư mục data
    if not os.path.exists("data"):
        print("❌ Không tìm thấy thư mục data")
        return False
    
    files = os.listdir("data")
    if not files:
        print("❌ Thư mục data trống")
        return False
    
    print(f"📁 Tìm thấy {len(files)} file trong data:")
    for file in files:
        print(f"  - {file}")
    
    try:
        # Xóa vectorstore cũ
        if os.path.exists("vectorstore"):
            shutil.rmtree("vectorstore")
            print("🗑️ Đã xóa vectorstore cũ")
        
        # Tạo RAG system
        print("🔄 Khởi tạo RAG system...")
        rag = LegalRAGSystem()
        
        # Xây dựng knowledge base
        print("🔄 Xây dựng knowledge base...")
        rag.build_knowledge_base()
        
        # Test hệ thống
        print("🔄 Test hệ thống...")
        result = rag.query("Văn bản này quy định về vấn đề gì?")
        
        if result["answer"] and "không tìm thấy" not in result["answer"].lower():
            print("✅ Knowledge base đã được xây dựng thành công!")
            print(f"📊 Tìm thấy {len(result['sources'])} nguồn tham khảo")
            print(f"📝 Câu trả lời mẫu: {result['answer'][:200]}...")
            return True
        else:
            print("⚠️ Có vấn đề với knowledge base")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    rebuild_knowledge_base()
