import re
from typing import Iterable, List, Optional
from app.models.schemas import CandidateResume, ExperienceItem


# Phone patterns: enforce boundaries and exact digit counts to avoid trailing capture
_PHONE_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"(?<!\d)0(?:[\s\-.]?\d){9}(?!\d)", re.UNICODE),         # 0 + 9 digits
    re.compile(r"(?<!\d)\+?84(?:[\s\-.]?\d){9}(?!\d)", re.UNICODE),    # +84 or 84 + 9 digits
]

_DATE_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b"),  # YYYY-MM-DD
    re.compile(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b"),  # DD-MM-YYYY or DD/MM/YY
]

_EXPERIENCE_SECTION_KEYS: List[str] = [
    "experience",
    "work experience",
    "employment",
    "professional experience",
    "kinh nghiệm",
    "kinh nghiem",
    "kinh nghiệm làm việc",
]

_DURATION_PATTERN: re.Pattern[str] = re.compile(
    r"\b(\d{4}|\d{2})\s*[–\-to]{1,2}\s*(\d{4}|\d{2}|present|nay|hiện tại|hien tai)\b",
    re.IGNORECASE,
)


def _normalize_phone(raw: str) -> str:
    digits: str = re.sub(r"\D", "", raw)
    # Convert +84 / 84 prefix to leading 0
    if digits.startswith("84"):
        remainder: str = digits[2:]
        digits = remainder if remainder.startswith("0") else ("0" + remainder)
    # Trim to 10 digits when starting with 0 (VN current standard)
    if digits.startswith("0") and len(digits) > 10:
        digits = digits[:10]
    # Fallback trim to 10 if longer
    if len(digits) > 10:
        digits = digits[:10]
    return digits


def _to_iso_date(raw: str) -> Optional[str]:
    for pattern in _DATE_PATTERNS:
        m = pattern.search(raw)
        if not m:
            continue
        groups: List[str] = list(m.groups())
        if pattern.pattern.startswith("\\b(\\d{4})"):
            year, month, day = groups
        else:
            day, month, year = groups
        if len(year) == 2:
            year = ("20" + year) if int(year) < 50 else ("19" + year)
        try:
            y: int = int(year)
            mth: int = int(month)
            d: int = int(day)
            if not (1 <= mth <= 12 and 1 <= d <= 31 and 1900 <= y <= 2100):
                continue
            return f"{y:04d}-{mth:02d}-{d:02d}"
        except ValueError:
            continue
    return None


def _extract_section_lines(text: str, section_keys: List[str], window: int = 50) -> List[str]:
    lower: str = text.lower()
    best_idx: int = -1
    for key in section_keys:
        idx: int = lower.find(key)
        if idx != -1:
            best_idx = idx
            break
    snippet: str = text if best_idx == -1 else text[best_idx : best_idx + 2000]
    lines: List[str] = [l.strip() for l in snippet.splitlines() if l.strip()]
    return lines[: window * 2]


def _extract_name(lines: List[str]) -> Optional[str]:
    for line in lines[:10]:
        if re.search(r"(name|họ\s*và\s*tên|ho\s*va\s*ten)\s*[:\-]", line, flags=re.IGNORECASE):
            candidate: str = re.sub(r"^(name|họ\s*và\s*tên|ho\s*va\s*ten)\s*[:\-]\s*", "", line, flags=re.IGNORECASE)
            candidate = re.sub(r"[^A-Za-zÀ-ỹ\s']", "", candidate).strip()
            if candidate:
                return candidate
    for line in lines[:5]:
        if len(line) <= 40 and re.fullmatch(r"[A-ZÀ-Ỹ\s']+", line.strip()):
            return line.title().strip()
    return None


def _extract_phone(text: str) -> Optional[str]:
    for pattern in _PHONE_PATTERNS:
        m = pattern.search(text)
        if m:
            return _normalize_phone(m.group(0))
    return None


def _extract_birth_date(text: str) -> Optional[str]:
    label_match = re.search(r"(dob|date\s*of\s*birth|ngày\s*sinh|ngay\s*sinh)\s*[:\-]?\s*(.*)", text, flags=re.IGNORECASE)
    if label_match:
        tail: str = label_match.group(2)[:20]
        iso: Optional[str] = _to_iso_date(tail)
        if iso:
            return iso
    return _to_iso_date(text)


def _extract_experience(lines: List[str]) -> List[ExperienceItem]:
    items: List[ExperienceItem] = []
    buffer: List[str] = []
    for line in lines:
        if _DURATION_PATTERN.search(line):
            if buffer:
                items.extend(_materialize_items(buffer))
                buffer = []
            buffer.append(line)
        else:
            if buffer:
                buffer.append(line)
    if buffer:
        items.extend(_materialize_items(buffer))
    return items[:10]


def _materialize_items(lines: List[str]) -> List[ExperienceItem]:
    text_block: str = " ".join(lines)
    duration: Optional[str] = None
    m = _DURATION_PATTERN.search(text_block)
    if m:
        duration = m.group(0)
    company: Optional[str] = None
    position: Optional[str] = None
    comp_match = re.search(r"(?:(?:at|@)\s+)?([A-Z][A-Za-z0-9&.,\-\s]{2,})", text_block)
    if comp_match:
        company = comp_match.group(1).strip().strip("-.,")
    pos_match = re.search(r"(position|title|role|chức danh|chuc danh)\s*[:\-]\s*([^;|.,]+)", text_block, flags=re.IGNORECASE)
    if pos_match:
        position = pos_match.group(2).strip()
    if not position:
        head: str = lines[0] if lines else ""
        head_clean: str = re.sub(r"\s*[-–]\s*" + re.escape(duration or ""), "", head).strip()
        if len(head_clean) <= 60:
            position = head_clean
    return [ExperienceItem(company=company, position=position, duration=duration)]


def extract_candidate_info(text: str) -> CandidateResume:
    lines: List[str] = [l for l in (s.strip() for s in text.splitlines()) if l]
    name: Optional[str] = _extract_name(lines)
    phone: Optional[str] = _extract_phone(text)
    birth_date: Optional[str] = _extract_birth_date(text)
    exp_lines: List[str] = _extract_section_lines(text=text, section_keys=_EXPERIENCE_SECTION_KEYS)
    experience: List[ExperienceItem] = _extract_experience(lines=exp_lines)
    return CandidateResume(name=name, phone=phone, birth_date=birth_date, experience=experience) 