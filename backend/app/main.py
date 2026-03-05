from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor

from app.routers import (
    literature,
    knowledge_add,
    settings,
    knowledge,
    review,
    translate,
    auth,
    chat,
)
from app.services.literature_service import delete_summary

app = FastAPI(title="科研助手后端", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(literature.router)
app.include_router(knowledge_add.router)
app.include_router(settings.router)
app.include_router(knowledge.router)
app.include_router(review.router)
app.include_router(translate.router)
app.include_router(auth.router)
app.include_router(chat.router)

executor = ThreadPoolExecutor()


@app.get("/")
async def read_root():
    return {"message": "欢迎使用科研助手后端！"}


@app.post('/delete_summary')
async def delete_summary_api(
    request: Request,
    id: int = Body(..., description="记录id"),
    user_id: str = Body(..., description="用户ID"),
):
    """
    删除综述生成记录
    """
    response = delete_summary(id)
    if response:
        return {"code": 200, "msg": "success", "data": None}
    return 0
