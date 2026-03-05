import re

from uvicorn import run
from api.api_bg import *
from api.api_fy import *

from fastapi import Query,BackgroundTasks,Body,Request,FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio

from subapi import get_from_oilink,add_to_knowledge,get_setting,get_knowledge,get_review,translate,system,llm_chat

# 创建 FastAPI 应用实例
app = FastAPI()


app.include_router(get_from_oilink.router)
app.include_router(add_to_knowledge.router)
app.include_router(get_setting.router)
app.include_router(get_knowledge.router)
app.include_router(get_review.router)
app.include_router(translate.router)
app.include_router(system.router)
app.include_router(llm_chat.router)



executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

# 配置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定 ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS、POST、GET 等
    allow_headers=["*"]   # 允许所有请求头
)



# 定义一个简单的根路径路由
@app.get("/")
async def read_root():
    return {"message": "欢迎使用 FastAPI 应用！"}








@app.post('/delete_summary')
async def delete_summary_api(
    request: Request,  # 添加 Request 对象以获取请求信息
    id: int = Body(..., description="记录id"),
    user_id: str = Body(..., description="用户ID"),#用于占位
):
    """
    删除综述生成记录
    :return:
    """
    response = delete_summary(id)
    if response:
        return {"code": 200, "msg": "success", "data": None}
    return 0







if __name__ == "__main__":
    print("科研助手应用已启动")
    # 启动 FastAPI 应用，开启 debug 模式实现代码热重载
    run("kyzs:app", host="0.0.0.0", port=8000, reload=True)
 