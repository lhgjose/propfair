from fastapi import FastAPI

app = FastAPI(
    title="PropFair API",
    description="Colombian Real Estate Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
