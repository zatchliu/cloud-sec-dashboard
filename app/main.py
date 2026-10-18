from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def root() -> dict[str, str]:
    return {"status" : "ok"}
