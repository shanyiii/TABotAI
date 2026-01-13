from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from google import genai

from mdSplitter import splitter
from config import GEMINI_API_KEY

embeddings = OpenAIEmbeddings()
COLLECTION_NAME = "qdrant_ch6_test"

def upload_to_qdrant():
    documents = splitter()

    vector_store = QdrantVectorStore.from_documents(
        documents=documents, 
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME,
        force_recreate=True,
    )
    print("===上傳完成===")

def qdrant_retrieval():
    vector_store = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    while True:
        user_question = input("今天想問什麼？輸入0以結束：")
        if user_question == "0":
            break
        
        knowledge = ""
        for result in vector_store.similarity_search(query=user_question):
            # knowledge = knowledge + f"{result.page_content}\n來源：{result.metadata}\n\n"
            knowledge = knowledge + f"{result.page_content}\n\n"
        # print(knowledge)
        print("="*30)

        # query = f"{knowledge}\n\n你是一個「軟體工程課程助教」請將以上資訊作為基礎知識，回答下列問題，並僅輸出你的回答：\n\n{user_question}"
        # client = genai.Client(api_key=GEMINI_API_KEY)
        # response = client.models.generate_content(
        #     model="gemini-2.5-flash-lite",
        #     contents=[
        #         query
        #     ])
        # print(response.text)

if __name__ == '__main__':
    # upload_to_qdrant()
    qdrant_retrieval()