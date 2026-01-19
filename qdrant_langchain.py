from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from google import genai

from file_processor import splitter
from config import GEMINI_API_KEY

embeddings = OpenAIEmbeddings()
COLLECTION_NAME = "qdrant_ch6_test"

async def upload_to_qdrant():
    documents = splitter()

    vector_store = QdrantVectorStore.from_documents(
        documents=documents, 
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME,
        force_recreate=True,
    )
    print("===上傳完成===")

async def qdrant_retrieval(user_question):
    vector_store = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    
    knowledge = ""
    for result in vector_store.similarity_search(query=user_question):
        # knowledge = knowledge + f"{result.page_content}\n來源：{result.metadata}\n\n"
        knowledge = knowledge + f"{result.page_content}\n\n"
        print(result.page_content)
        print("="*30)
    print("===Retrieval completed===")

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
    # upload_to_qdrant()
    qdrant_retrieval()