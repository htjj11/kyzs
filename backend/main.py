from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor

from routers import (
    数据检索,
    个人知识库,
    公共知识库,
    报告,
    翻译,
    系统配置,
)
from services.report_service import delete_summary

app = FastAPI(title="科研助手后端", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(数据检索.router)
app.include_router(个人知识库.router)
app.include_router(公共知识库.router)
app.include_router(报告.router)
app.include_router(翻译.router)
app.include_router(系统配置.router)
 

executor = ThreadPoolExecutor()


@app.get("/")
async def read_root():
    return {"message": "欢迎使用科研助手后端！"}




if __name__ == "__main__":
    import threading
    import uvicorn
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    import functools
    import os
    import ssl

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 证书路径（放在backend目录下）
    cert_path = os.path.join(base_dir, "cert_2.pem")
    key_path  = os.path.join(base_dir, "10.68.202.238_RSA.key")

    # 自定义 Handler：支持 SPA history 模式路由回退
    # 等同于 Nginx 的 try_files $uri $uri/ /index.html
    class SPAHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split('?')[0]  # 去掉 query string
            # URL 解码（处理中文文件名如 /assets/公共知识库主页-xxx.js）
            try:
                import urllib.parse
                decoded_path = urllib.parse.unquote(path)
            except Exception:
                decoded_path = path
            if decoded_path == '/':
                decoded_path = '/index.html'
            full_path = os.path.join(self.directory, decoded_path.lstrip('/'))
            if not os.path.isfile(full_path):
                # 静态文件不存在 → 回退到 index.html（SPA 路由）
                self.path = '/index.html'
            return super().do_GET()

    def run_frontend():
        handler = functools.partial(
            SPAHandler,
            directory=os.path.join(base_dir,"frontend")
        )
        server = ThreadingHTTPServer(("0.0.0.0", 443), handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print("前端服务运行在 https://0.0.0.0:443")
        server.serve_forever()

    t = threading.Thread(target=run_frontend, daemon=True)
    t.start()

    # FastAPI 走 HTTPS 8443 端口
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8443,
        ssl_certfile=cert_path,
        ssl_keyfile=key_path,
        reload=True
    )