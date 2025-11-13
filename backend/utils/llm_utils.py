import os
from openai import OpenAI
from utils.config import NVIDIA_API_KEY, NVIDIA_LLM_MODEL, NVIDIA_LLM_BASE_URL, debug_log
from openai import OpenAI

client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_LLM_BASE_URL)

def call_llm(messages, max_tokens=90000):

    print(f"Calling llm model")
    completion = client.chat.completions.create(
        model=NVIDIA_LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=max_tokens,
    )
    content = completion.choices[0].message.content.strip()
    print(f"llm done, Output length: {len(content)} chars")
    return content
