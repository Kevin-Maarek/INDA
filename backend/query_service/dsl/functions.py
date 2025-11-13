import pandas as pd
import json
from typing import Any, Dict, List
import numpy as np
from utils.embedding_utils import get_embedding
from utils.qdrant_utils import search_points, SERVICE_HE_FIELD
from utils.config import debug_log, QDRANT_COLLECTION
from utils.llm_utils import call_llm
from qdrant_client import QdrantClient

qdrant = QdrantClient()

# make sure the context is a DataFrame
def ensure_df(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, list):
        return pd.DataFrame(data)
    raise ValueError("Unsupported context type")

# ----------------------fatch and filter----------------------------------- #

# get all feedbacks from Qdrant
def fetch_all_feedbacks(limit: int = 10000) -> pd.DataFrame:
    debug_log(f"Fetching feedbacks...")
    results = qdrant.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=None,
        limit=limit,
        with_payload=True,
    )
    points = results[0]
    df = pd.DataFrame([p.payload for p in points])
    debug_log(f"Fetched {len(df)} rows")
    return df

# filter feedbacks by Level field
def filter_by_level(data: pd.DataFrame, operator: str, value: int) -> pd.DataFrame:
    df = ensure_df(data)
    ops = {
        "lt": df["Level"] < value,
        "lte": df["Level"] <= value,
        "eq": df["Level"] == value,
        "gte": df["Level"] >= value,
        "gt": df["Level"] > value,
    }
    filtered = df[ops[operator]].copy()
    debug_log(f"{len(filtered)}/{len(df)} rows after Level {operator} {value}")
    return filtered

# find the correct service name using semantic search
def resolve_service_name(service_name: str, top_k: int = 3):
    debug_log(f"finding semantecly that correct service name using user query:'{service_name}'")
    vector = get_embedding(service_name)
    if not vector:
        debug_log("failed to create embedding")
        return []

    results = search_points(vector, vector_name="service_vector", top_k=top_k)
    names = [
        r.payload.get(SERVICE_HE_FIELD)
        for r in results
        if r.payload and r.payload.get(SERVICE_HE_FIELD)
    ]
    debug_log(f"found the service name:: {names}" if names else f"no match for '{service_name}'")
    return names

# filter feedbacks by service name
def filter_by_service(data: pd.DataFrame, service_name: str) -> pd.DataFrame:
    df = ensure_df(data)
    resolved_names = resolve_service_name(service_name)

    if resolved_names:
        filtered = df[df["service_demended_hebrew"].isin(resolved_names)]
    else:
        filtered = df[df["service_demended_hebrew"].str.contains(service_name, case=False, na=False)]

    debug_log(f"Filtered {len(filtered)} rows with the service name '{service_name}'")
    return filtered

# filter feedbacks by text containing keyword
def filter_by_text_contains(data: pd.DataFrame, keyword: str) -> pd.DataFrame:
    df = ensure_df(data)
    mask = df["text"].astype(str).str.contains(keyword, case=False, na=False)
    debug_log(f"filtered by keyword '{keyword}': {mask.sum()} matches")
    return df[mask].copy()

# filter feedbacks by text containing keyword using semantic search
def filter_by_text_semantic(context, query: str):
    df = ensure_df(context)
    query = (query or "").strip()
    if not query:
        return df


    q_vec = get_embedding(query, input_type="query")
    if not q_vec:
        return df.head(0)

    TOP_K = 1500

    res = search_points(
        vector=q_vec,
        vector_name="text_vector",
        top_k=TOP_K
    )

    if not res:
        return df.head(0)


    scored = [(r, float(getattr(r, "score", 0.0))) for r in res]
    scored.sort(key=lambda x: x[1], reverse=True)

    scores = [s for (_, s) in scored]
    max_score = scores[0]

    threshold = max_score * 0.80

    filtered = [(r, s) for (r, s) in scored if s >= threshold]

    if len(filtered) < 5:
        threshold *= 0.90
        filtered = [(r, s) for (r, s) in scored if s >= threshold]

    MIN_RESULTS = 20
    if len(filtered) < MIN_RESULTS:
        filtered = scored[:MIN_RESULTS]

    rows = []
    for r, s in filtered:
        payload = r.payload or {}
        rows.append({
            "ID": payload.get("ID"),
            "text": payload.get("text"),
            "Level": payload.get("Level"),
            "service_demended_hebrew": payload.get("service_demended_hebrew"),
            "CreationDate": payload.get("CreationDate"),
            "score": s,
        })

    new_df = pd.DataFrame(rows).sort_values(by="score", ascending=False).reset_index(drop=True)

    return new_df

# group feedbacks by service and apply aggregation
def group_by_service(data: pd.DataFrame, calc: str = "count", field: str = "Level"):
    df = ensure_df(data)
    if df is None or df.empty:
        debug_log("no data for grouping")
        return df

    debug_log(f"grouping by service (calc={calc}, field={field})")
    agg_map = {
        "avg": "mean",
        "sum": "sum",
        "count": "count",
        "max": "max",
        "min": "min",
    }

    if calc == "none":
        grouped = (
            df.groupby("service_demended_hebrew")[field]
              .apply(list)
              .reset_index()
              .rename(columns={field: f"{field}_list"})
        )
    elif calc in agg_map:
        grouped = (
            df.groupby("service_demended_hebrew")[field]
              .agg(agg_map[calc])
              .reset_index()
              .rename(columns={field: f"{calc}_{field}"})
        )
    else:
        raise ValueError(f"unknown calc: {calc}")

    debug_log(f"grouped {len(grouped)} rows")
    return grouped


# sort feedbacks by a field
def sort_results(data: pd.DataFrame, order: str = "asc", field: str = None) -> pd.DataFrame:
    df = ensure_df(data)
    if not field:
        field = df.columns[-1]
    sorted_df = df.sort_values(by=field, ascending=(order == "asc"))
    debug_log(f"sorted by {field} ({order})", "↕️")
    return sorted_df

def count_records(context=None, **kwargs):
    df = ensure_df(context)
    count = len(df)

    return pd.DataFrame([{"total_count": count}])


# filter feedbacks by level
def filter_by_value(data: pd.DataFrame, field: str, operator: str, value: float) -> pd.DataFrame:
    df = ensure_df(data)
    ops = {
        "lt": df[field] < value,
        "lte": df[field] <= value,
        "eq": df[field] == value,
        "gte": df[field] >= value,
        "gt": df[field] > value,
    }
    filtered = df[ops[operator]].copy()
    debug_log(f"{len(filtered)} rows after {field} {operator} {value}")
    return filtered

# get list of texts from feedbacks dataframe
def get_texts(df):
    debug_log("Extracting texts from DataFrame")
    if isinstance(df, dict) and "data" in df:
        df = ensure_df(df["data"])

    df = ensure_df(df)

    texts = df["text"].dropna().astype(str).tolist()
    return {"texts": texts}


# -----------------------llm and semantic functions---------------------------------- #

def semantic_dynamic(context=None, prompt: str = "", texts: List[str] = None):

    if texts is None:
        if isinstance(context, dict) and "texts" in context:
            texts = context["texts"]
        elif isinstance(context, dict) and "data" in context:
            df = ensure_df(context["data"])
            texts = df["text"].dropna().astype(str).tolist()
        elif hasattr(context, "to_dict"):
            df = ensure_df(context)
            texts = df["text"].dropna().astype(str).tolist()
        else:
            return {"error": "לא נמצאו טקסטים לניתוח"}

    if not texts:
        return {"error": "לא נמצאו טקסטים לניתוח"}

    joined_texts = "\n".join(texts)

    schema_system = (
        "You are a Schema Planning LLM. "
        "You receive a Hebrew question from the user. "
        "Your task: design the IDEAL JSON structure for the answer. "
        "The schema must:\n"
        "1. Be a valid JSON.\n"
        "2. Define all keys the second LLM should return.\n"
        "3. Define value types: string, number, list[string], list[number], object, list[object].\n"
        "4. Be minimal but expressive.\n"
        "5. Never include markdown or code fences.\n"
        "6. Return ONLY the schema JSON.\n"
    )

    schema_user = f"""
    השאלה של המשתמש:
    "{prompt}"

    צור סכמה אידיאלית (JSON) עבור התשובה לשאלה הזאת.
    """

    schema_messages = [
        {"role": "system", "content": schema_system},
        {"role": "user", "content": schema_user}
    ]

    try:
        schema_raw = call_llm(schema_messages, max_tokens=90000)
        schema_clean = schema_raw.strip().replace("```json", "").replace("```", "").strip()
        schema = json.loads(schema_clean)
    except Exception as e:
        return {"error": f"Schema creation failed: {e}", "raw": schema_raw}

    analyst_system = (
"""
You are an advanced Hebrew-speaking analytics engine.

🎯 Your ONLY output format is VALID JSON.
❗ Absolutely NO markdown, no code fences, no backticks.
❗ Output must begin with `{` and end with `}`.
❗ Keys must be consistent and meaningful.
❗ Values must NEVER be plain Python repr (no single quotes) — ONLY standard JSON.

When asked to analyze feedback, summarize, classify, extract topics, generate answers, or produce responses — you MUST:

1. Return a structured JSON object with clear keys.
2. Prefer arrays of objects rather than long free text.
3. Use this JSON structure unless told otherwise:

{
  "summary": "<text summary>",
  "items": [
    {
      "title": "...",
      "description": "...",
      "analysis": "...",
      "score": <number or null>,
      "extra": {...}
    }
  ]
}

For tasks involving matching feedback to responses (e.g., "תן ביקורות ומענה"):
Return this structure exactly:

{
  "reviews": [
    {
      "review_text": "<the feedback text>",
      "response": "<the recommended answer>"
    }
  ],
  "total_reviews": <number>
}

All text must be valid UTF-8 and structured.

Do NOT return raw dict-like output (e.g., {'x':1}).
Do NOT return keys in Hebrew unless they represent user-facing data.
Do NOT invent your own inconsistent structure. Follow the templates.
"""

    )

    analyst_user = f"""
    השאלה: "{prompt}"

    הסכמה:
    {json.dumps(schema, ensure_ascii=False)}

    הטקסטים לניתוח:
    {joined_texts[:50000]} 

    החזר JSON תקני התואם בדיוק את הסכמה.
    """

    analyst_messages = [
        {"role": "system", "content": analyst_system},
        {"role": "user", "content": analyst_user},
    ]

    try:
        answer_raw = call_llm(analyst_messages, max_tokens=100000)
        answer_clean = answer_raw.strip().replace("```json", "").replace("```", "").strip()
        answer = json.loads(answer_clean)
        return answer
    except Exception as e:
        return {"error": f"Answer creation failed: {e}", "raw": answer_raw}


# ------------------------rendering result--------------------------------- #

# render feedbacks dataframe as a table
def render_table(context, columns=None):
    if isinstance(context, dict) and "data" in context:
        df = context["data"]
    else:
        df = context  

    if df is None or df.empty:
        debug_log("⚠️ אין נתונים להצגה")
        return {"type": "table", "data": []}

    if not columns:
        columns = df.columns.tolist()

    existing_cols = [c for c in columns if c in df.columns]
    df = df[existing_cols]

    debug_log(f"מציג {len(df)} שורות × {len(df.columns)} עמודות")
    return {"type": "table", "data": df.to_dict(orient="records")}


# render text summary
def render_text(context=None, **kwargs):
    print(f"rendering text from context: {type(context),} this is the value in context var: {context}")

    if isinstance(context, dict):
        if "type" in context:
            return context

        if any(k in context for k in ["summary", "main_issues", "recommendations", "sentiment", "topics"]):
            return context

        return {"type": "text", "content": str(context)}

    if isinstance(context, str):
        return {"type": "text", "content": context}

    if isinstance(context, list):
        joined = "\n".join(map(str, context))
        return {"type": "text", "content": joined}

    return {"type": "text", "content": str(context)}



# ----------------------functuins dic----------------------------------- #

DSL_FUNCTIONS = {
    "resolve_service_name": resolve_service_name,
    "fetch_all_feedbacks": fetch_all_feedbacks,
    "filter_by_level": filter_by_level,
    "filter_by_service": filter_by_service,
    "filter_by_text_contains": filter_by_text_contains,
    "group_by_service": group_by_service,
    "sort_results": sort_results,
    "filter_by_value": filter_by_value,
    "get_texts": get_texts,
    "render_table": render_table,
    "render_text": render_text,
    "count_records": count_records,
    "semantic_dynamic": semantic_dynamic,
    "filter_by_text_semantic": filter_by_text_semantic,
}
