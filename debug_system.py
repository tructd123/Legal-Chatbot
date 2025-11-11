#!/usr/bin/env python3
"""
Debug script for Legal RAG System
"""

import os
from dotenv import load_dotenv
from legal_rag import LegalRAGSystem

# Load environment variables
load_dotenv()

def debug_system():
    """Debug the system step by step"""
    print("🔍 DEBUGGING LEGAL RAG SYSTEM")
    print("=" * 50)
    
    # 1. Check API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ GOOGLE_API_KEY: {api_key[:10]}...")
    else:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    # 2. Check vector store files
    print(f"\n📁 Checking vector store files:")
    vectorstore_path = "vectorstore/legal_faiss"
    if os.path.exists(vectorstore_path):
        files = os.listdir(vectorstore_path)
        print(f"   Files found: {files}")
        
        # Check file sizes
        for file in files:
            file_path = os.path.join(vectorstore_path, file)
            size = os.path.getsize(file_path)
            print(f"   {file}: {size} bytes")
    else:
        print(f"   ❌ Vector store path not found: {vectorstore_path}")
        return
    
    # 3. Initialize system
    print(f"\n🔄 Initializing Legal RAG System...")
    try:
        rag = LegalRAGSystem()
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # 4. Load knowledge base
    print(f"\n📚 Loading knowledge base...")
    try:
        success = rag.load_knowledge_base()
        if success:
            print("✅ Knowledge base loaded")
        else:
            print("❌ Failed to load knowledge base")
            return
    except Exception as e:
        print(f"❌ Error loading knowledge base: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Check vector store content
    print(f"\n🔍 Checking vector store content...")
    if rag.vector_store:
        try:
            # Get total number of vectors
            total_vectors = rag.vector_store.index.ntotal
            print(f"   Total vectors: {total_vectors}")
            
            # Test similarity search with simple terms
            test_queries = ["luật", "nghị định", "bảo hiểm", "quy định"]
            
            for query in test_queries:
                print(f"\n   Testing search for: '{query}'")
                docs = rag.vector_store.similarity_search(query, k=3)
                print(f"   Found {len(docs)} documents")
                
                for i, doc in enumerate(docs):
                    print(f"     Doc {i+1}:")
                    print(f"       Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"       Content preview: {doc.page_content[:100]}...")
                    print(f"       Content length: {len(doc.page_content)}")
        except Exception as e:
            print(f"❌ Error checking vector store: {e}")
            import traceback
            traceback.print_exc()
    
    # 6. Test QA chain
    print(f"\n🤖 Testing QA Chain...")
    if rag.qa_chain:
        print("✅ QA Chain exists")
        print(f"   Input keys: {rag.qa_chain.input_keys}")
        print(f"   Output keys: {rag.qa_chain.output_keys}")
        
        # Test with simple question
        test_question = "luật là gì"
        print(f"\n   Testing with question: '{test_question}'")
        
        try:
            result = rag.query(test_question)
            print(f"   ✅ Query successful")
            print(f"   Answer length: {len(result['answer'])}")
            print(f"   Answer preview: {result['answer'][:200]}...")
            print(f"   Sources found: {len(result['sources'])}")
            
            if result['sources']:
                print(f"   First source:")
                source = result['sources'][0]
                print(f"     File: {source['source']}")
                print(f"     Content: {source['content'][:100]}...")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ QA Chain not initialized")
    
    print(f"\n" + "=" * 50)
    print("🔍 DEBUG COMPLETED")
    
    # 2. Kiểm tra imports
    try:
        from legal_rag import LegalRAGSystem
        from document_processor import LegalDocumentProcessor
        print("2. Imports: ✅ OK")
    except Exception as e:
        print(f"2. Imports: ❌ {e}")
        return
    
    # 3. Kiểm tra data folder
    if os.path.exists("data"):
        files = os.listdir("data")
        print(f"3. Data folder: ✅ {len(files)} files found")
        for file in files:
            print(f"   - {file}")
    else:
        print("3. Data folder: ❌ Not found")
        return
    
    # 4. Test document processor
    try:
        processor = LegalDocumentProcessor()
        documents = processor.process_documents("data")
        print(f"4. Document processing: ✅ {len(documents)} chunks created")
        
        if documents:
            print(f"   - First chunk preview: {documents[0].page_content[:100]}...")
            print(f"   - First chunk metadata: {documents[0].metadata}")
    except Exception as e:
        print(f"4. Document processing: ❌ {e}")
        return
    
    # 5. Test RAG system creation
    try:
        rag = LegalRAGSystem()
        print("5. RAG system creation: ✅ OK")
    except Exception as e:
        print(f"5. RAG system creation: ❌ {e}")
        return
    
    # 6. Test knowledge base building
    try:
        rag.build_knowledge_base()
        print("6. Knowledge base building: ✅ OK")
    except Exception as e:
        print(f"6. Knowledge base building: ❌ {e}")
        return
    
    # 7. Test vector store
    if rag.vector_store:
        try:
            docs = rag.vector_store.similarity_search("nghị định", k=3)
            print(f"7. Vector store search: ✅ Found {len(docs)} documents")
            if docs:
                print(f"   - Sample result: {docs[0].page_content[:100]}...")
        except Exception as e:
            print(f"7. Vector store search: ❌ {e}")
    else:
        print("7. Vector store: ❌ Not initialized")
        return
    
    # 8. Test QA chain
    if rag.qa_chain:
        print("8. QA chain: ✅ Initialized")
    else:
        print("8. QA chain: ❌ Not initialized")
        return
    
    # 9. Test queries
    test_questions = [
        "Nghị định này quy định về vấn đề gì?",
        "Mục đích của văn bản pháp luật này là gì?",
        "Ai là người ký nghị định này?"
    ]
    
    print("9. Testing queries:")
    for i, question in enumerate(test_questions, 1):
        try:
            result = rag.query(question)
            answer_preview = result["answer"][:100] if result["answer"] else "No answer"
            sources_count = len(result["sources"])
            print(f"   {i}. Q: {question}")
            print(f"      A: {answer_preview}...")
            print(f"      Sources: {sources_count}")
            print()
        except Exception as e:
            print(f"   {i}. Error: {e}")
    
    print("=" * 50)
    print("DEBUG COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    debug_system()
