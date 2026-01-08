from fastapi import FastAPI
from propfair_api.routers import listings, analysis, auth

app = FastAPI(
    title="PropFair API",
    description="Colombian Real Estate Intelligence Platform",
    version="0.1.0",
)

app.include_router(listings.router)
app.include_router(analysis.router)
app.include_router(auth.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
