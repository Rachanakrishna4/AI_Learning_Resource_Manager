from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, Response

from schemas import ResourceCreate, SearchRequest
from services.llm_service import generate_answer
from services.retrieval_service import search_notes
from services.database_service import (
    init_db,
    create_resource as db_create_resource,
    get_all_resources as db_get_all_resources,
    get_resource as db_get_resource,
    update_resource as db_update_resource,
    delete_resource as db_delete_resource,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Study Companion", lifespan=lifespan)


@app.get("/")
def home():
    index_file = Path(__file__).parent / "static" / "index.html"
    if not index_file.exists():
        raise HTTPException(500, "UI file static/index.html was not found")
    return FileResponse(index_file)


@app.post("/resources", status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceCreate):
    return db_create_resource(resource.model_dump(mode="json"))


@app.get("/resources")
def get_resources():
    return db_get_all_resources()


@app.get("/resources/{resource_id}")
def get_resource(resource_id: int):
    resource = db_get_resource(resource_id)
    if resource is None:
        raise HTTPException(404, "Resource not found")
    return resource


@app.put("/resources/{resource_id}")
def update_resource(resource_id: int, resource: ResourceCreate):
    updated = db_update_resource(resource_id, resource.model_dump(mode="json"))
    if updated is None:
        raise HTTPException(404, "Resource not found")
    return updated


@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int):
    if not db_delete_resource(resource_id):
        raise HTTPException(404, "Resource not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/search")
def search_resources(request: SearchRequest):
    try:
        results = search_notes(question=request.question, top_k=request.top_k)
    except ValueError as error:
        raise HTTPException(400, str(error))
    return {
        "question": request.question,
        "results_found": len(results),
        "results": results,
    }


@app.post("/ask")
def ask_question(request: SearchRequest):
    try:
        passages = search_notes(question=request.question, top_k=request.top_k)
        answer = generate_answer(question=request.question, passages=passages)
    except ValueError as error:
        raise HTTPException(400, str(error))
    except RuntimeError as error:
        raise HTTPException(502, str(error))

    sources = [
        {
            "source": p.get("source", "Unknown"),
            "chunk_index": p.get("chunk_index"),
            "distance": p.get("distance"),
        }
        for p in passages
    ]
    return {"question": request.question, "answer": answer, "sources": sources}