from fastapi import FastAPI
import uvicorn


app = FastAPI()

@app.get("/hello")
def read_root():
    return {"message": "Hello, FastAPI!"}

# 添加新的路由
@app.get("/hello/{name}")
def read_item(name: str):
    return {"message": f"Hello, {name}!"}

# 添加搜索路由
@app.get("/search/{item}")
def search_item(item: str):
    return {"message": f"You searched for {item}!"}

if __name__ == "__main__":
    # 启动服务
    uvicorn.run(app, host="127.0.0.1", port=5573)