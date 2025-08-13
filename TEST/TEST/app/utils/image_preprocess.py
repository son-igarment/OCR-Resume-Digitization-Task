from typing import Optional
import io
import numpy as np
from PIL import Image
import cv2


def load_image_to_numpy(file_bytes: bytes) -> np.ndarray:
    image: Image.Image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return np.array(image)


def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced: np.ndarray = clahe.apply(gray)
    thr: np.ndarray = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thr 