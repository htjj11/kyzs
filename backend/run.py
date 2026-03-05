from uvicorn import run

if __name__ == "__main__":
    print("科研助手应用已启动")
    run("app.main:app", host="0.0.0.0", port=8000, reload=True)
