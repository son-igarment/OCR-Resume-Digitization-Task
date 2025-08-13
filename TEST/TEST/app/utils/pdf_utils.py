from typing import List
import io
import fitz  # PyMuPDF
import numpy as np
from PIL import Image


def convert_pdf_to_images(file_bytes: bytes, dpi: int = 200) -> List[np.ndarray]:
    images: List[np.ndarray] = []
    zoom: float = dpi / 72.0
    mat: fitz.Matrix = fitz.Matrix(zoom, zoom)
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(np.array(img))
    return images 