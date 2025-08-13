Handwritten Resume Digitization Platform (MVP)
Goal
The API accepts a handwritten resume as an image (JPG/PNG) or PDF, then:

Converts PDF to images (if needed)
Preprocesses images to improve OCR quality
Runs OCR (EasyOCR, EN + VI)
Extracts fields: full name, phone number, date of birth, work experience
Returns structured JSON via schema
Tech Stack
FastAPI (Python) – REST API
EasyOCR (CPU) – OCR in English + Vietnamese
PyMuPDF – render PDF → images
OpenCV + Pillow – image loading and preprocessing
Pydantic v2 – data schemas
Project Structure
The source lives inside TEST/ (within the project root):

