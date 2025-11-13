import os
import uuid
import pandas as pd
from tqdm import tqdm
from typing import Dict
from utils.embedding_utils import get_embedding
from utils.qdrant_utils import upsert_point
from utils.llm_utils import call_llm
from utils.config import debug_log

from qdrant_client.models import VectorParams, Distance
from utils.config import QDRANT_COLLECTION
from qdrant_client import QdrantClient

qdrant = QdrantClient()
VECTOR_SIZE = 2048

# check and create collection if not exists
def ensure_collection_exists():
    try:
        qdrant.get_collection(QDRANT_COLLECTION)
        print(f"Collection '{QDRANT_COLLECTION}' already exists.")
    except Exception:
        print(f"Creating new collection '{QDRANT_COLLECTION}'...")
        qdrant.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config={
                "text_vector": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                "service_vector": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            },
        )

# split service_demended to service name and service office and translate service names to Hebrew using LLM
def translate_service_names(df: pd.DataFrame) -> pd.DataFrame:
    col = next((c for c in df.columns if c.lower() == "servicename"), None)
    if not col:
        return df

    df["service_demended"] = df[col].apply(lambda x: x.split("@")[0] if isinstance(x, str) and "@" in x else x)
    services = df["service_demended"].dropna().unique().tolist()

    translations = {}
    for s in tqdm(services):
        prompt = f"""You are a professional translator and data normalization assistant working for an Israeli government feedback analytics system.

                    You receive a *service name* written in CamelCase or mixed English form (for example: `App4aBirthCertificate`, `CannabisRequest`, `AppointmentForVisas`, `AgraPikuahAviri`).
                    Each service name refers to a real Israeli government service, form, or online process.

                    Your task:
                    1. **Translate** the given service name into clear, fluent, and natural **Hebrew**.
                    2. The translation must sound like the *official service name* as it would appear on gov.il or in a government app.
                    3. Do **not** return explanations, phonetic transliterations, or code-style names.
                    4. If the name contains abbreviations (like “App4a”), try to infer the intent (for example, “App4aBirthCertificate” to “בקשה לתעודת לידה”).
                    5. Output only the final Hebrew phrase — **no extra text, punctuation, or quotes**.

                    Example translations:
                    - `App4aBirthCertificate` → בקשה לתעודת לידה  
                    - `AppointmentForVisas` → זימון תור לוויזה  
                    - `CannabisRequest` → בקשה לרישיון קנאביס רפואי  
                    - `AgraPikuahAviri` → אגרת פיקוח אווירי  
                    - `ApprovedImporter` → יבואן מאושר

                    Now translate the following service name to clear Hebrew only:
                    {s}"""
        try:
            result = call_llm([{"role": "user", "content": prompt}], max_tokens=9000)
            translations[s] = result.strip()
        except Exception as e:
            print(f"error in translate {s}: {e}")
            translations[s] = s

    df["service_demended_hebrew"] = df["service_demended"].map(translations)
    print("done translating service names to Hebrew")
    return df

# main function to process CSV and upload to Qdrant
def process_csv_to_qdrant(csv_path: str) -> Dict[str, int]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(csv_path)
    ensure_collection_exists()
    df = translate_service_names(df)

    for i, row in df.iterrows():
        text = str(row.get("Text", "")).strip()
        service = str(row.get("service_demended_hebrew", "")).strip()

        try:
            text_vec = get_embedding(text, input_type="passage")
            service_vec = get_embedding(service, input_type="passage")

            payload = row.to_dict()
            payload.pop("Text", None)

            upsert_point(
                point_id=str(uuid.uuid4()),
                vector_dict={"text_vector": text_vec, "service_vector": service_vec},
                payload={**payload, "text": text}
            )
            debug_log(f"Indexed {service}")
        except Exception as e:
            print(f"error in line {i}: {e}")
            continue

    print(f"done, {len(df)} feedbacks indexed to Qdrant")
    return {"inserted": len(df)}
