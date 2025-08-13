from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_415_UNSUPPORTED_MEDIA_TYPE
from app.models.schemas import CandidateResume, ExperienceItem
from app.services.ocr_service import ocr_images
from app.services.parsing_service import extract_candidate_info
from app.utils.pdf_utils import convert_pdf_to_images
from app.utils.image_preprocess import load_image_to_numpy


router: APIRouter = APIRouter()


@router.post("/extract-resume", response_model=CandidateResume)
async def extract_resume(file: UploadFile = File(...)) -> CandidateResume:
    content_type: Optional[str] = file.content_type
    if content_type is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Missing content type")

    is_image: bool = content_type in {"image/jpeg", "image/png", "image/jpg"}
    is_pdf: bool = content_type == "application/pdf"

    if not (is_image or is_pdf):
        raise HTTPException(status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")

    file_bytes: bytes = await file.read()

    images: List = []
    if is_pdf:
        images = convert_pdf_to_images(file_bytes=file_bytes, dpi=220)
    else:
        images = [load_image_to_numpy(file_bytes=file_bytes)]

    ocr_text: str = ocr_images(images=images)
    resume: CandidateResume = extract_candidate_info(text=ocr_text)
    return resume 