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

load_dotenv()

VECTOR_DB_SRC = os.environ["VECTOR_DB_SRC"]
VECTOR_DB_DIR = os.environ["VECTOR_DB_DIR"]
VECTOR_DB_INDEX_NAME = os.environ["VECTOR_DB_INDEX_NAME"]
PATH_SPLIT = os.environ["PATH_SPLIT"]


def load_pdf_data() -> (list, list):
    """
    Load all PDFs in the VECTOR_DB_SRC directory.
    Args:
        None.

    Returns:
        str: Two lists. One contains the PDF text, the other is the PDF meta data.
    """
    loader = PyPDFDirectoryLoader(VECTOR_DB_SRC)
    docs = loader.load()

    texts = []
    metas = []

    for doc in docs:
        doc.metadata["source"] = doc.metadata["source"].split(PATH_SPLIT)[1]
        texts.append(doc.page_content)
        metas.append(doc.metadata)
    logging.info(f"# docs: {len(docs)}, # metas: {len(metas)}")
    return texts, metas


def create_vector_db() -> FAISS:
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
        embeddings = OpenAIEmbeddings()
        texts, metas = load_pdf_data()
        db = FAISS.from_texts(texts=texts, metadatas=metas, embedding=embeddings)
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
