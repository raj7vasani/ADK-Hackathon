from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.pipelines.query_router import handle_user_query

app = FastAPI(title="ADK-Hackathon Data Collector")

class QueryBody(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(body: QueryBody):
    try:
        result = handle_user_query(body.query)
        return {"status": "success", "data": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
