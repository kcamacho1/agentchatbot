import os
import PyPDF2
from docx import Document
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json
import hashlib
from datetime import datetime

class DocumentProcessor:
    """Handles document processing, storage, and retrieval for the chatbot"""
    
    def __init__(self, documents_dir: str = "documents", processed_dir: str = "processed"):
        self.documents_dir = documents_dir
        self.processed_dir = processed_dir
        self.vector_db_path = os.path.join(processed_dir, "vector_db")
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        
        # Create collections for different document types
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Ensure directories exist
        os.makedirs(documents_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        
        # Load document metadata
        self.metadata_file = os.path.join(processed_dir, "document_metadata.json")
        self.document_metadata = self.load_metadata()
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load document metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_metadata(self):
        """Save document metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.document_metadata, f, indent=2)
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for file to track changes"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error processing DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error processing TXT {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def process_document(self, file_path: str) -> bool:
        """Process a single document and add to vector database"""
        try:
            # Get file info
            file_name = os.path.basename(file_path)
            file_hash = self.get_file_hash(file_path)
            
            # Check if already processed with same hash
            if file_name in self.document_metadata:
                if self.document_metadata[file_name]['hash'] == file_hash:
                    print(f"Document {file_name} already processed and up to date")
                    return True
            
            # Extract text based on file type
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self.extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                text = self.extract_text_from_txt(file_path)
            else:
                print(f"Unsupported file type: {file_ext}")
                return False
            
            if not text.strip():
                print(f"No text extracted from {file_name}")
                return False
            
            # Chunk the text
            chunks = self.chunk_text(text)
            
            # Create embeddings and store in vector database
            embeddings = self.embedding_model.encode(chunks)
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_{i}"
                chunk_ids.append(chunk_id)
                chunk_metadata.append({
                    "file_name": file_name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_type": file_ext,
                    "processed_date": datetime.now().isoformat()
                })
            
            # Add to vector database
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            # Update metadata
            self.document_metadata[file_name] = {
                "hash": file_hash,
                "processed_date": datetime.now().isoformat(),
                "total_chunks": len(chunks),
                "file_type": file_ext,
                "file_size": os.path.getsize(file_path)
            }
            
            self.save_metadata()
            print(f"Successfully processed {file_name} into {len(chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def process_all_documents(self) -> Dict[str, bool]:
        """Process all documents in the documents directory"""
        results = {}
        
        for filename in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, filename)
            if os.path.isfile(file_path):
                results[filename] = self.process_document(file_path)
        
        return results
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents for relevant content"""
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of processed documents"""
        summary = {
            "total_documents": len(self.document_metadata),
            "documents": self.document_metadata,
            "vector_db_size": len(self.collection.get()['ids']) if self.collection.count() > 0 else 0
        }
        return summary 