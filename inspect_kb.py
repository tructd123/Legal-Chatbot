from legal_rag import LegalRAGSystem
rag = LegalRAGSystem()
rag.load_knowledge_base()
docs = rag.vector_store.similarity_search("Đối tượng áp dụng luật đấu thầu", k=3)
for d in docs:
    print("---", d.metadata)
    print(d.page_content[:500])
exit()