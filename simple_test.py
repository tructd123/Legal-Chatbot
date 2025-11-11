#!/usr/bin/env python3
"""
Simple test for Legal RAG System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔑 Checking environment variables...")
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"✅ GOOGLE_API_KEY found: {api_key[:10]}...")
else:
    print("❌ GOOGLE_API_KEY not found")
    exit(1)

print("\n📚 Testing Legal RAG System...")

try:
    from legal_rag import LegalRAGSystem
    
    # Khởi tạo hệ thống
    print("🔄 Initializing system...")
    rag = LegalRAGSystem()
    
    # Load knowledge base
    print("📖 Loading knowledge base...")
    if rag.load_knowledge_base():
        print("✅ Knowledge base loaded successfully!")
        
        # Debug chain
        print("\n🔍 Debugging chain:")
        test_question = "Cần lưu ý những điều gì khi cho vay?"
        debug_info = rag.debug_chain_inputs(test_question)
        print(f"👉 Prompt preview:\n{debug_info['prompt'][:500]}...\n")

        # Test với câu hỏi đơn giản
        print("\n❓ Testing with simple question...")
        result = rag.query(test_question)
        
        print(f"📝 Answer: {result['answer'][:200]}...")
        print(f"📋 Sources: {len(result['sources'])}")
        
        if result['sources']:
            print("\n📚 First source:")
            source = result['sources'][0]
            print(f"   File: {source['source']}")
            print(f"   Content: {source['content'][:100]}...")
        
        print("\n✅ Test completed successfully!")
    else:
        print("❌ Failed to load knowledge base")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
