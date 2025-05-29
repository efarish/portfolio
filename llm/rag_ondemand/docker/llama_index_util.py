import os

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI
from s3fs import S3FileSystem

S3_BUCKET = os.environ.get("S3_BUCKET")
AWS_KEY = os.environ.get("AWS_KEY")
AWS_SECRET = os.environ.get("AWS_SECRET")

S3_FS = S3FileSystem(
    key=AWS_KEY,
    secret=AWS_SECRET,
    client_kwargs={'region_name': 'us-east-1'}
    # asynchronous=True,
    # loop=asyncio.get_running_loop(),
)

async def _get_doc_nodes(s3_files_dir):
    docs = await SimpleDirectoryReader(fs=S3_FS, input_dir=s3_files_dir).aload_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(docs)
    return nodes


async def create_index(session_id: str, recreate=False):

    s3_dir = S3_BUCKET + "/" + session_id
    s3_files_dir = s3_dir + "/files"
    s3_summary_index_dir = s3_dir + "/summary"
    s3_vector_index_dir = s3_dir + "/vector"

    summary_exits = S3_FS.exists(s3_summary_index_dir)
    vector_exists = S3_FS.exists(s3_vector_index_dir)

    if not (summary_exits and vector_exists) or recreate:

        nodes = await _get_doc_nodes(s3_files_dir)

        summary_index = SummaryIndex(nodes, use_async=True)
        vector_index = VectorStoreIndex(nodes, use_async=True)

        summary_index.storage_context.persist(
            fs=S3_FS, persist_dir=s3_summary_index_dir
        )
        vector_index.storage_context.persist(fs=S3_FS, persist_dir=s3_vector_index_dir)


async def query(session_id: str, query: str):

    s3_dir = S3_BUCKET + "/" + session_id
    s3_summary_index_dir = s3_dir + "/summary"
    s3_vector_index_dir = s3_dir + "/vector"

    storage_context = StorageContext.from_defaults(
        fs=S3_FS, persist_dir=s3_summary_index_dir
    )
    summary_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        fs=S3_FS, persist_dir=s3_vector_index_dir
    )
    vector_index = load_index_from_storage(storage_context)

    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )

    vector_query_engine = vector_index.as_query_engine()

    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_query_engine",
        query_engine=summary_query_engine,
        description=("Useful for summarization questions related to this document."),
    )

    vector_tool = QueryEngineTool.from_defaults(
        name=f"vector_query_engine",
        query_engine=vector_query_engine,
        description=("Useful for retrieving specific context from this document."),
    )

    llm = OpenAI(model="o4-mini", temperature=0)

    agent = FunctionAgent(
        name="A multi-tool agent",
        description="An agent that answers questions about documents.",
        tools=[vector_tool, summary_tool],
        llm=llm,
        system_prompt=(
            "You are a research agent answering questions based on the context provided. "
            "Only use your tools and the context they provide to answer questions."
        )
    )

    response = await agent.run(query)

    return str(response)
