"""API tối thiểu cho hai pipeline AI của DocAI."""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status

from docai.shared.config import settings
from docai.shared.schema import DocumentType, UnifiedDocumentOutput

app = FastAPI(title=settings.api_title, version=settings.api_version)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "docai", "version": settings.api_version}


@app.post("/parse/classic", response_model=UnifiedDocumentOutput, tags=["AI"])
async def parse_classic(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(default=DocumentType.INVOICE),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Track A inference chưa được triển khai.",
    )


@app.post("/parse/vlm", response_model=UnifiedDocumentOutput, tags=["AI"])
async def parse_vlm(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(default=DocumentType.INVOICE),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Track B inference chưa được triển khai.",
    )
