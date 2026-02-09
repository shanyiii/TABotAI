import os
from typing import List

from haystack import Document, Pipeline
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from neo4j_haystack import Neo4jEmbeddingRetriever, Neo4jDocumentStore

from file_processor import md_splitter
from config import OPENAI_API_KEY, NEO4J_PASSWORD

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

document_store = Neo4jDocumentStore(
    url="neo4j://localhost:7687",
    username="neo4j",
    password=NEO4J_PASSWORD,
    database="neo4j",
    embedding_dim=384,
    index="document-embeddings",
)

def upload_to_neo4j(documents: list):
    document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")  
    document_embedder.warm_up()
    documents_with_embeddings = document_embedder.run(documents)

    document_store.write_documents(documents_with_embeddings.get("documents"))

    print(document_store.count_documents())


async def neo4j_retriever(question: str) -> str:
    template = [
        ChatMessage.from_user(
            """
            你是一個「軟體工程課程助教」請根據提供的資訊用台灣繁體中文回答問題，並僅輸出你的回答。如果問題與「軟體工程」無關，或是答案無法從資訊得知的話，請不要擅自生成答案。

            Context:
            {% for document in documents %}
                {{ document.content }}
            {% endfor %}

            Question: {{question}}
            Answer:
            """
        )
    ]

    prompt_builder = ChatPromptBuilder(template=template, required_variables=["question"])
    gpt_chat = OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o-mini")

    pipeline = Pipeline()
    pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
    pipeline.add_component("retriever", Neo4jEmbeddingRetriever(document_store=document_store))
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", gpt_chat)

    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    pipeline.connect("retriever.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder.prompt", "llm.messages")

    result = pipeline.run(
        data={
            "text_embedder": {"text": question}, 
            "prompt_builder": {"question": question}
        },
        include_outputs_from=["retriever", "llm"]
    )

    return result["llm"]["replies"][0]._content[0].text

if __name__ == '__main__':
    try:
        with open("md_files\\marker_test_output.md", 'r', encoding='utf-8') as input_file:
            md_content = input_file.read()
    except FileNotFoundError:
        print("Error: The specified file was not found.")

    md_documents = md_splitter(md_content)
    documents = [Document(content=doc.page_content) for doc in md_documents]

    upload_to_neo4j(documents)

    # res = neo4j_retriever("請問有哪些git指令可以做分支合併？")
    # print(res)
    # retrieved_docs = res["retriever"]["documents"]
    # for doc in retrieved_docs:
    #     print(doc.content[:200])
    # print("="*30)
    # print(res["llm"]["replies"][0]._content[0].text)