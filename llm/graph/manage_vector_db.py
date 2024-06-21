"""
A script for creating a vector data store using FAISS.

Any PDF placed in the ./data directory is used to create an index.
"""
import logging
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from typing import List

load_dotenv()

VECTOR_DB_SRC =        os.environ["VECTOR_DB_SRC"]
VECTOR_DB_DIR =        os.environ["VECTOR_DB_DIR"]
VECTOR_DB_INDEX_NAME = os.environ["VECTOR_DB_INDEX_NAME"]

def create_vector_db(docs:List[Document] = None) -> FAISS:
    """
    Create a FAISS vector data store if one does not exist.
    If the vector store has already been created, load it and return it.
    Args:
        None.

    Returns:
        str: FAISS instance.
    """
    embeddings = OpenAIEmbeddings()
    if not os.path.exists(VECTOR_DB_DIR):
        logging.warning("Source directory doesn't exists. Create vector data store...")
        if docs is None or len(docs) == 0:
            raise Exception("No documents provided. Can't create data store.")
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(docs, embeddings)
        db.save_local(index_name=VECTOR_DB_INDEX_NAME, folder_path=VECTOR_DB_DIR)
        logging.info("Done.")
    else:
        logging.info("Data source exists. Loading vector data store.")
        db = FAISS.load_local(
            index_name=VECTOR_DB_INDEX_NAME,
            embeddings=embeddings,
            folder_path=VECTOR_DB_DIR,
            allow_dangerous_deserialization=True,
        )
    return db


def get_retriever(k: int) -> VectorStoreRetriever:
    """
    Gets a Chroma retriever.
    Args: k - the number of documents to retrieve.
    Returns: VectorStoreRetriever instance.
    """
    db = create_vector_db()
    return db.as_retriever(search_kwargs={"k": k})


def main():
    db = create_vector_db()
    logging.warning(f"Documents found in vector DB: {db.index.ntotal}")


if __name__ == "__main__":
    main()
