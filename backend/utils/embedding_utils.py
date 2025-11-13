from utils.config import NVIDIA_API_KEY, NVIDIA_EMBED_MODEL, NVIDIA_EMBED_BASE_URL, debug_log
from openai import OpenAI

client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_EMBED_BASE_URL)


def get_embedding(text: str, input_type="query"):

    print(f"[Generating embedding for: '{text}...'")
    response = client.embeddings.create(
        input=[text],
        model=NVIDIA_EMBED_MODEL,
        encoding_format="float",
        extra_body={"input_type": input_type, "truncate": "NONE"},
    )
    vector = response.data[0].embedding
    print(f"MBEDDING DONE length={len(vector)}")
    return vector
