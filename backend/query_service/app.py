from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query_service.dsl.interpreter import interpret_question_to_dsl
from query_service.dsl.executor import execute_dsl_flow
from fastapi.middleware.cors import CORSMiddleware
import traceback

app = FastAPI(title="Query Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    status: str
    dsl: dict
    result: dict

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):

    question = req.question.strip()
    print(f"\nnew user query: {question}")

    try:
        dsl_plan = interpret_question_to_dsl(question)
        if "error" in dsl_plan:
            raise Exception("DSL interpretation failed")

        result = execute_dsl_flow(dsl_plan)
        print(f"the DSL flow is: {result}")

        return {
            "status": "success",
            "dsl": dsl_plan,
            "result": result,
        }

    except Exception as e:
        print(f"error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
