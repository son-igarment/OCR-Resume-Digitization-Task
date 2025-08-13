from typing import List, Optional
import threading
import numpy as np
import easyocr
from app.utils.image_preprocess import preprocess_for_ocr


_reader_lock: threading.Lock = threading.Lock()
_reader_instance: Optional[easyocr.Reader] = None


def _get_reader() -> easyocr.Reader:
    global _reader_instance
    if _reader_instance is not None:
        return _reader_instance
    with _reader_lock:
        if _reader_instance is None:
            # English + Vietnamese for resumes in VN context
            _reader_instance = easyocr.Reader(["en", "vi"], gpu=False)
    return _reader_instance


def ocr_images(images: List[np.ndarray]) -> str:
    if len(images) == 0:
        return ""
    reader: easyocr.Reader = _get_reader()
    page_texts: List[str] = []
    for image in images:
        processed: np.ndarray = preprocess_for_ocr(image=image)
        lines: List[str] = reader.readtext(processed, detail=0, paragraph=True)
        page_texts.append("\n".join(lines))
    return "\n\n".join(page_texts) 