from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool


def get_doc_nodes(file_name):
    docs = SimpleDirectoryReader(input_files=[file_name]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(docs)
    return nodes

def get_doc_tools(file_name: str, name_suffix: str):

    index_loaded = False

    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=f"./storage/{name_suffix}_summary"
        )
        summary_index = load_index_from_storage(storage_context)

        storage_context = StorageContext.from_defaults(
            persist_dir=f"./storage/{name_suffix}_vector"
        )
        vector_index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        print('Indexes not found.')
        
    if not index_loaded:
        nodes = get_doc_nodes(file_name)
        summary_index = SummaryIndex(nodes)
        vector_index = VectorStoreIndex(nodes)

        summary_index.storage_context.persist(persist_dir=f"./storage/{name_suffix}_summary")
        vector_index.storage_context.persist(persist_dir=f"./storage/{name_suffix}_vector")

    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )

    summarization_response = summary_query_engine.query("Please provide a concise sentence that summarizes the document.")

    vector_query_engine = vector_index.as_query_engine()

    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_query_engine_{name_suffix}",
        query_engine=summary_query_engine,
        description=(
            "Useful for summarization questions related to this document which is about: " + str(summarization_response)
        ),
    )
    vector_tool = QueryEngineTool.from_defaults(
        name=f"vector_query_engine_{name_suffix}",
        query_engine=vector_query_engine,
        description=(
            "Useful for retrieving specific context from this document which is about: " + str(summarization_response)
        ),
    )

    return vector_tool, summary_tool

