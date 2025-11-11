import os 
import PyPDF2
import pdfplumber
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from typing import List

class LegalDocumentProcessor:
    def __init__(self): 
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def read_pdf(self, file_path: str) -> str: 
        text = ''
        # Try pdfplumber first
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            if text.strip():
                print(f"✅ Extracted text with pdfplumber ({len(text)} chars)")
                return text
        except Exception as e:
            print(f"⚠️ pdfplumber failed for {file_path}: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            if text.strip():
                print(f"✅ Extracted text with PyPDF2 ({len(text)} chars)")
                return text
        except Exception as e:
            print(f"⚠️ PyPDF2 failed for {file_path}: {e}")
        
        print(f"❌ No text extracted from {file_path}. Might be a scanned PDF.")
        return ""
    
    def read_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).replace("\ufeff", "")
    
    def read_txt(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read().replace("\ufeff", "")

    def process_documents(self, data_folder: str) -> List[LangchainDocument]:
        documents = []
        total_chunks = 0
        
        for filename in os.listdir(data_folder):
            file_path = os.path.join(data_folder, filename)
            ext = filename.split('.')[-1].lower()

            try: 
                if filename.endswith('.pdf'):
                    text = self.read_pdf(file_path)
                elif filename.endswith('.docx'):
                    text = self.read_docx(file_path)
                elif filename.endswith('.txt'):
                    text = self.read_txt(file_path)
                else: 
                    print(f"⚠️ Skipping unsupported file type: {filename}")
                    continue

                if not text.strip():
                    print(f"⚠️ No text extracted from {filename}, skipping.")
                    continue

                # Split into chunks
                chunks = self.text_splitter.split_text(text)
                total_chunks += len(chunks)

                for i, chunk in enumerate(chunks):
                    documents.append(LangchainDocument(
                        page_content=chunk, 
                        metadata={
                            "source": filename,
                            "chunk_index": i,
                            "document_type": ext
                        }
                    ))
                print(f"📄 Processed {filename} → {len(chunks)} chunks")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
        
        print(f"✅ Done! Total documents: {len(documents)} chunks across all files.")
        return documents

if __name__ == "__main__":
    processor = LegalDocumentProcessor()
    docs = processor.process_documents("data")  # Thư mục chứa PDF/DOCX/TXT
    print(f"Loaded {len(docs)} chunks.")
    if docs:
        print(docs[0].page_content[:300])  # Preview nội dung chunk đầu tiên
        print(docs[0].metadata)
    else:
        print("No documents were processed.")