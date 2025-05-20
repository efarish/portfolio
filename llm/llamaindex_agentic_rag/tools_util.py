from llama_index.core import SimpleDirectoryReader, SummaryIndex, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool


def get_doc_tools(file_names: str,name_suffix: str):

    docs = SimpleDirectoryReader(input_files=[file_names]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(docs)

    summary_index = SummaryIndex(nodes)
    vector_index = VectorStoreIndex(nodes)

    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    vector_query_engine = vector_index.as_query_engine()

    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_query_engine_{name_suffix}",
        query_engine=summary_query_engine,
        description=(
            "Useful for summarization questions related to the document."
        ),
    )
    vector_tool = QueryEngineTool.from_defaults(
        name=f"vector_query_engine_{name_suffix}",
        query_engine=vector_query_engine,
        description=(
            "Useful for retrieving specific context from the document."
        ),
    )

    return vector_tool, summary_tool

