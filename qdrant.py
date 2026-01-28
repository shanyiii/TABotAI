from qdrant_client import QdrantClient, models
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from google import genai
from tqdm import tqdm
from uuid import uuid4

from file_processor import md_splitter, get_tags_from_gpt, build_tag_alias_map, tag_to_embedding_text
from config import GEMINI_API_KEY
from common import COLLECTION_NAME, QDRANT_URL, COURSE_NAME, TAG_COLLECTION_NAME

# 連線到資料庫
client = QdrantClient(url=QDRANT_URL)

# embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = OpenAIEmbeddings()
# VECTOR_SIZE = embeddings.get_sentence_embedding_dimension()

def upload_to_db(tag_map):
    # 如果 collection 不存在就建立一個
    if not client.collection_exists(TAG_COLLECTION_NAME):
        client.create_collection(
            collection_name=TAG_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                )
        )

    points = list()
    for tag, info in tag_map.items():
        text = tag_to_embedding_text(tag, info["aliases"])
        vector = embeddings.embed_query(text)

        points.append(
            models.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "label": tag,
                    "aliases": list(info["aliases"])
                },
            )
        )

    client.upsert(
        collection_name=TAG_COLLECTION_NAME,
        points=points,
    )

    print("===上傳完成===")

async def retrieval(user_question):
    query_vector = embeddings.embed_query(user_question)

    tag_hits = client.query_points(
        collection_name=TAG_COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    matched_tags = [hit.payload["label"] for hit in tag_hits]
    print("Matched tags: ", matched_tags)

    if not matched_tags:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5
        )

    else:
        filter_by_tags = models.Filter(
            should=[
                models.FieldCondition(
                    key="metadata.tags",
                    match=models.MatchAny(any=matched_tags)
                )
            ]
        )

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5,
            query_filter=filter_by_tags
        ).points

    return results

async def response_from_ai(user_question):
    results = await retrieval(user_question)
    knowledge = ""
    for result in results:
        knowledge = knowledge + f"{result.payload['page_content']}\n\n"
        print(result.payload['page_content'])
        print("===tags===\n",result.payload['metadata']['tags'])
        print("="*30)
    print("===Retrieval completed===")
    
    query = f"資訊：\n{knowledge}\n\n你是一個「軟體工程課程助教」請將以上資訊作為基礎知識，回答問題，並僅輸出你的回答。如果問題與「軟體工程」無關，或是答案無法從以上資訊得知的話，請回答「無法回答」，並附上原因。\n\n問題：{user_question}"
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            query
        ])

    return response.text

if __name__ == '__main__':
    try:
        with open("md_files\\marker_test_output.md", 'r', encoding='utf-8') as input_file:
            md_content = input_file.read()
    except FileNotFoundError:
        print("Error: The specified file was not found.")

    md_documents = md_splitter(md_content)

    documents = list()
    title_lists = list()
    tag_lists = list()
    print("===start chunk tags extraction===")
    for doc in md_documents:
        chunk_tags = get_tags_from_gpt(COURSE_NAME, "學術概念", doc.page_content)
        titles = [value for value in doc.metadata.values()]
        title_lists.append(titles)
        tag_lists.append(chunk_tags['tags'])
    print("===extraction finished===")

    tag_map = build_tag_alias_map(tag_lists, title_lists)

    upload_to_db(tag_map)