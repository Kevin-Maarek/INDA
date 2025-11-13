from fastapi import FastAPI, UploadFile, File, HTTPException
from indexing_service.indexing_worker import process_csv_to_qdrant
import tempfile
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Indexing Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest_csv")
async def ingest_csv(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = process_csv_to_qdrant(tmp_path)
        os.remove(tmp_path)
        print(f"Indexed file {file.filename} successfully.")
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
