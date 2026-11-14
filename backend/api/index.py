from fastapi import FastAPI
app = FastAPI()

@app.get("/api/{path:path}")
def handle_api(path: str):
    return {"message": f"API endpoint: {path}"}
