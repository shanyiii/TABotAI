from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from google import genai
from uuid import uuid4
import json

from file_processor import md_splitter
from config import GEMINI_API_KEY, QDRANT_API_KEY

from ollama import chat

def get_tags_doc_level(doc_text):
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': '你是一位專業的「軟體工程」課程助教，請為以下教材內容提取3個「檔案層級」的關鍵字標籤，以JSON格式輸出 {"tags": ["A", "B", "C"]}'},
        {'role': 'user', 'content': doc_text}
    ], format='json') 
    return response['message']['content']

def get_tags_chunk_level(doc_text):
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': '你是一位專業的「軟體工程」課程助教，請為以下文本內容提取3個學術概念關鍵字標籤，以JSON格式輸出 {"tags": ["A", "B", "C"]}'},
        {'role': 'user', 'content': doc_text}
    ], format='json') 
    return response['message']['content']

embeddings = OpenAIEmbeddings()
COLLECTION_NAME = "qdrant_ch6_test"
QDRANT_URL = "https://086b08d2-7e0e-48f6-89af-28f97ec29e85.europe-west3-0.gcp.cloud.qdrant.io"

async def upload_to_qdrant():
    # creating a new collection

    vector_store = QdrantVectorStore.from_documents(
        documents=documents, 
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        force_recreate=True,
        prefer_grpc=True,
    )

    # upload to existing collection

    # qdrant = QdrantVectorStore.from_existing_collection(
    #     embedding=embeddings,
    #     collection_name=COLLECTION_NAME,
    #     url=QDRANT_URL,
    # )
    # uuids = [str(uuid4()) for _ in range(len(documents))]
    # vector_store.add_documents(documents=documents, ids=uuids)

    print("===上傳完成===")

async def qdrant_retrieval(user_question):
    vector_store = QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    
    knowledge = ""
    print("\n===Start retrieval===\n")
    for result in vector_store.similarity_search(query=user_question):
        # knowledge = knowledge + f"{result.page_content}\n來源：{result.metadata}\n\n"
        knowledge = knowledge + f"{result.page_content}\n\n"
        print(result.page_content)
        print("="*30)
    print("\n===Retrieval completed===\n")

    query = f"{knowledge}\n\n你是一個「軟體工程課程助教」請將以上資訊作為基礎知識，回答問題，並僅輸出你的回答。如果問題與「軟體工程」無關，或是答案無法從以上資訊得知的話，請不要擅自產生答案。\n\n問題：{user_question}"
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            query
        ])

    return response.text
    # print(response.text)

if __name__ == '__main__':
    with open("md_files/shorter_markdown_test.md", 'r', encoding='utf-8') as input_file:
        md_content = input_file.read()
    
    doc_tags_json = get_tags_doc_level(md_content)   # tags at document level
    doc_tags_dict = json.loads(doc_tags_json)
    print("[debug] document level tags: ", doc_tags_dict)
    print("="*30)

    documents = md_splitter(md_content)  # splitting document into chunks
    for doc in documents:
        chunk_tags_json = get_tags_chunk_level(doc.page_content)
        chunk_tags_dict = json.loads(doc_tags_json)
        print("[debug] chunk level tags: ", chunk_tags_dict)

    # upload_to_qdrant()
    # qdrant_retrieval()