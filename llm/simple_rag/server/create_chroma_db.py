import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
from load_data_from_bible import *
import logging

def create_chroma_db():
    load_dotenv()
    if not os.path.exists( os.environ['VECTOR_DB_SRC'] ):
        logging.warning("Chroma source directory doesn't exists. Create embeddings...")
        embeddings = OpenAIEmbeddings()
        batch_size = 10
        texts, metas = get_doc_meta_list()
        for i in tqdm( range(0, len(texts), batch_size) ):
            db = Chroma.from_texts(texts=texts[i:i+batch_size],
                                metadatas=metas[i:i+batch_size],
                                embedding=embeddings,
                                persist_directory=os.environ['VECTOR_DB_SRC'])    
        logging.info("Done.")    
        return texts, metas
    else: logging.warning('Chroma source directory already exists. No need to create embeddings.')

def main():
    create_chroma_db()
    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory=os.environ['VECTOR_DB_SRC'], embedding_function=embeddings)
    docs = db.get()
    cnt = len(docs['ids'])
    logging.warning(f'Documents found in vector DB: {cnt}')

if __name__ == '__main__':
    main()


