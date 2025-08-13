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

TEST/
  app/
    main.py
    routers/
      extract_resume.py
    services/
      ocr_service.py
      parsing_service.py
    utils/
      pdf_utils.py
      image_preprocess.py
    models/
      schemas.py
    middleware/
      error_handler.py
  tests/
    test_parsing.py
  requirements.txt
  README.md
System Requirements
Python 3.10+
Windows 10/11 (recommended; also works on macOS/Linux)
Installation (Windows/PowerShell)
Work in the correct source directory (C:\Users\ASUS\Desktop\TEST\TEST):

cd C:\Users\ASUS\Desktop\TEST\TEST
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
If torch is difficult to install on Windows (CPU-only):

python -m pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
Then install the remaining dependencies if needed:

python -m pip install -r requirements.txt
Run the Server
Run from C:\Users\ASUS\Desktop\TEST\TEST (where app/ resides):

uvicorn app.main:app --reload --port 8000
Open: http://127.0.0.1:8000 (auto-redirects to Swagger docs at /docs).

Main API
POST /extract-resume
Content-Type: multipart/form-data
Field: file
Supports: image/jpeg, image/png, application/pdf
PowerShell example using the curl alias:

curl -X POST http://127.0.0.1:8000/extract-resume ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@C:\\path\\to\\your\\resume.jpg"
Sample response:

{
  "name": "Nguyen Van A",
  "phone": "0901234567",
  "birth_date": "1995-07-20",
  "experience": [
    { "company": "ABC Manufacturing", "position": "Operator", "duration": "2021–2023" }
  ]
}
Note: If a field cannot be extracted, values may be null and experience may be empty.

Testing
Run inside the virtual environment and correct source directory (TEST/ inner folder):

cd C:\Users\ASUS\Desktop\TEST\TEST
python -m pytest -q
Troubleshooting
PowerShell may block venv activation:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
torch installation errors: use the CPU wheel as shown above, or consult the PyTorch installation matrix.
Poor OCR on blurry/tilted images: increase PDF render DPI (e.g., dpi >= 220), use sharp, high-contrast scans.
Deployment Notes
Root endpoint / redirects to /docs.
OCR reader is cached in-process to speed up subsequent calls.
Short Roadmap
Improve heuristics for company/position extraction in experience.
Add deskew and adaptive thresholding to preprocessing.
Optional OCR warm-up on startup via lifespan for better cold-start latency.
