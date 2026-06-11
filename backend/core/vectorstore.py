from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import time
from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()

class VectorStoreManager:
    def __init__(self, collection_name="financial_docs"):

        # Free, local, no rate limits
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.persist_directory = "data/vectorstore"
        self.collection_name = collection_name
        os.makedirs(self.persist_directory, exist_ok=True)

        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def add_documents(self, documents):
        self.vector_db.add_documents(documents)
        print(f"[ChromaDB] Added {len(documents)} chunks to {self.persist_directory}")

    def search(self, query, k=10):
        return self.vector_db.similarity_search(query, k=k)

    def as_retriever(self, k=10):
        return self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def is_empty(self):
        return self.vector_db._collection.count() == 0

    def clear(self):
        self.vector_db.delete_collection()
        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("Vectorstore cleared.")

    def get_stored_files(self) -> list:
        # return the list of unique filenames from the database
        try:
            results = self.vector_db.get()
            filenames =  set()
            for meta in results["metadatas"]:
                if meta.get("file_names"):
                    filenames.add(meta["file_names"])
            return list(filenames)
        except:
            return []
        
    def remove_file(self,filename:str):
        # remove all the chunks associated with file
        try:
            results = self.vector_db.get()
            ids_to_delete = [
                results["id"][i]
                for i,meta in enumerate(results["metadatas"])
                if meta.get("file_name") == filename
            ]
            if ids_to_delete:
                self.vector_db.delete(ids=ids_to_delete)
                print(f"[CHROMADB] Removed {len(ids_to_delete)} chunks for {filename}")
        except Exception as e:
            print(f"[CHROMAB] Remove failed {e}")


    def clear(self):
        # wipe out entire collection 
        self.vector_db.delete_collection()
        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function= self.embedding_function,
            persist_directory = self.persist_directory
        )
        print("[CHROMADB ] Cleared")