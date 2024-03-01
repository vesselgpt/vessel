from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import ocr

app = FastAPI(openapi_url="/api/v1/vessel-ocr/openapi.json", docs_url="/api/v1/vessel-ocr/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(ocr.router, prefix="/api/v1/vessel-ocr", tags=["Vessel OCR"])


@app.get("/")
async def root():
    return {"message": "Vessel OCR API"}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

# run the app with: python api.py
# go to http://127.0.0.1:8000/api/v1/vessel-ocr/docs to see the Swagger UI