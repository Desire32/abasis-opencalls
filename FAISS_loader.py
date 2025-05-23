import os
import faiss
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

class FAISSLoader:
    def __init__(self, folder_path="pdfs", model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.folder_path = folder_path
        self.model_name = model_name

        self.docs = []
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        self.texts = []
        self.vectors = []
        self.index = None
        self.vectorstore = None

        self.load_pdfs()
        self.build_index()

    def load_pdfs(self):
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                filepath = os.path.join(self.folder_path, filename)
                loader = PyPDFLoader(filepath)
                docs = loader.load()

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=200
                )
                split_docs = splitter.split_documents(docs)

                self.docs.extend(split_docs)

    def build_index(self):
        texts = [doc.page_content for doc in self.docs]
        self.texts = texts
        self.vectors = [self.embeddings.embed_query(text) for text in texts]

        dim = len(self.vectors[0])
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(self.vectors))

        docstore = InMemoryDocstore()
        id_map = {}

        for i, doc in enumerate(self.docs):
            doc_id = str(i)
            docstore._dict[doc_id] = doc
            id_map[i] = doc_id

        self.vectorstore = FAISS(
            embedding_function=self.embeddings,
            index=self.index,
            docstore=docstore,
            index_to_docstore_id=id_map
        )

        print("FAISS index successfully built and stored in memory.")

    def search(self, query, k=3):
        """Search for relevant documents using the query."""
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

if __name__ == "__main__":
    loader = FAISSLoader(folder_path="pdfs")
    # Test search
    # results = loader.search("What are the eligibility criteria?")
    # for i, result in enumerate(results, 1):
    #     print(f"\nResult {i}:")
    #     print(result)

