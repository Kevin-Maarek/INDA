from utils.config import QDRANT_URL, QDRANT_COLLECTION, debug_log
from qdrant_client import QdrantClient

qdrant = QdrantClient(url=QDRANT_URL)

SERVICE_HE_FIELD = "service_demended_hebrew"


def search_points(vector, vector_name="service_vector", top_k=5):

    print(f"QDRANT SEARCH vector='{vector_name}', limit={top_k}")
    results = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=(vector_name, vector),
        with_payload=True,
        limit=top_k,
    )
    print(f"QDRANT Found {len(results)} results.")
    return results


def upsert_point(point_id, vector_dict, payload):

    print(f"QDRANT UPSERT id={point_id} vectors={list(vector_dict.keys())}")
    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            {
                "id": point_id,
                "vector": vector_dict,
                "payload": payload,
            }
        ],
    )
    print("UPSERT DONE")


def delete_collection():

    print(f"QDRANT DELETE Dropping collection {QDRANT_COLLECTION}")
    qdrant.delete_collection(collection_name=QDRANT_COLLECTION)
