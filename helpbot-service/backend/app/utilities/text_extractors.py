"""Baseline text extractors for PDF, DOCX, Markdown, HTML, TXT, VTT, and SRT files.

Each extractor returns normalized full text plus lightweight structural segments
(page number, heading, or transcript timestamp range). This keeps the ingestion
pipeline ready for future chunk-level semantic retrieval and transcript linking.
"""

from __future__ import annotations

import io
import re
from dataclasses import asdict, dataclass

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.exceptions import ValidationError


@dataclass(frozen=True)
class ExtractedSegment:
    """Represents a logical section, page, or timestamped cue within a document."""

    text: str
    page_or_section: str | None = None
    timestamp_range: str | None = None


@dataclass(frozen=True)
class ExtractionResult:
    """Normalized extraction output persisted in KnowledgeContent."""

    full_text: str
    segments: list[ExtractedSegment]

    def segments_as_dicts(self) -> list[dict[str, str | None]]:
        return [asdict(segment) for segment in self.segments]


_VTT_TIMESTAMP_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s*-->\s*"
    r"(?P<end>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})"
)
_SRT_TIMESTAMP_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)
_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def _decode_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValidationError("Unable to decode text file as UTF-8.", code="decode_error")


def _extract_pdf(raw_bytes: bytes) -> ExtractionResult:
    try:
        reader = PdfReader(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise ValidationError(f"Could not parse PDF file: {exc}", code="parse_error") from exc

    segments: list[ExtractedSegment] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            segments.append(ExtractedSegment(text=text, page_or_section=f"Page {index}"))
    full_text = "\n\n".join(seg.text for seg in segments).strip()
    return ExtractionResult(full_text=full_text, segments=segments)


def _extract_docx(raw_bytes: bytes) -> ExtractionResult:
    try:
        doc = DocxDocument(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise ValidationError(f"Could not parse DOCX file: {exc}", code="parse_error") from exc

    segments: list[ExtractedSegment] = []
    current_heading = "Document Body"
    buffer: list[str] = []

    def _flush() -> None:
        if buffer:
            segments.append(
                ExtractedSegment(text="\n".join(buffer).strip(), page_or_section=current_heading)
            )
            buffer.clear()

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = (para.style.name or "").lower() if para.style else ""
        if style_name.startswith("heading"):
            _flush()
            current_heading = text
        else:
            buffer.append(text)
    _flush()

    # Include table text if present
    for table_idx, table in enumerate(doc.tables, start=1):
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            segments.append(
                ExtractedSegment(
                    text="\n".join(rows),
                    page_or_section=f"Table {table_idx}",
                )
            )

    full_text = "\n\n".join(seg.text for seg in segments).strip()
    return ExtractionResult(full_text=full_text, segments=segments)


def _extract_markdown(raw_bytes: bytes) -> ExtractionResult:
    text = _decode_text(raw_bytes)
    segments: list[ExtractedSegment] = []
    current_heading = "Introduction"
    buffer: list[str] = []

    def _flush() -> None:
        body = "\n".join(buffer).strip()
        if body:
            segments.append(ExtractedSegment(text=body, page_or_section=current_heading))
        buffer.clear()

    for line in text.splitlines():
        match = _MD_HEADING_RE.match(line.strip())
        if match:
            _flush()
            current_heading = match.group(2).strip()
        else:
            buffer.append(line)
    _flush()

    full_text = "\n\n".join(seg.text for seg in segments).strip()
    return ExtractionResult(full_text=full_text, segments=segments)


def _extract_html(raw_bytes: bytes) -> ExtractionResult:
    html_text = _decode_text(raw_bytes)
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    segments: list[ExtractedSegment] = []
    current_heading = soup.title.get_text(strip=True) if soup.title else "Page Content"
    buffer: list[str] = []

    def _flush() -> None:
        body = "\n".join(buffer).strip()
        if body:
            segments.append(ExtractedSegment(text=body, page_or_section=current_heading))
        buffer.clear()

    body_root = soup.body or soup
    for element in body_root.find_all(["h1", "h2", "h3", "h4", "p", "li", "tr"]):
        text = element.get_text(" ", strip=True)
        if not text:
            continue
        if element.name in {"h1", "h2", "h3", "h4"}:
            _flush()
            current_heading = text
        else:
            buffer.append(text)
    _flush()

    if not segments:
        fallback = soup.get_text("\n", strip=True)
        if fallback:
            segments.append(ExtractedSegment(text=fallback, page_or_section=current_heading))

    full_text = "\n\n".join(seg.text for seg in segments).strip()
    return ExtractionResult(full_text=full_text, segments=segments)


def _extract_plain_text(raw_bytes: bytes) -> ExtractionResult:
    text = _decode_text(raw_bytes).strip()
    segments = [ExtractedSegment(text=text, page_or_section="Full Text")] if text else []
    return ExtractionResult(full_text=text, segments=segments)


def _extract_transcript(raw_bytes: bytes, is_vtt: bool) -> ExtractionResult:
    text = _decode_text(raw_bytes)
    pattern = _VTT_TIMESTAMP_RE if is_vtt else _SRT_TIMESTAMP_RE
    segments: list[ExtractedSegment] = []

    current_range: str | None = None
    cue_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_range
        body = " ".join(line.strip() for line in cue_lines if line.strip()).strip()
        if body:
            segments.append(
                ExtractedSegment(
                    text=body,
                    page_or_section="Transcript",
                    timestamp_range=current_range,
                )
            )
        cue_lines.clear()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            _flush()
            current_range = None
            continue
        if is_vtt and (line.upper().startswith("WEBVTT") or line.startswith("NOTE")):
            continue
        match = pattern.match(line)
        if match:
            _flush()
            start = match.group("start").replace(",", ".")
            end = match.group("end").replace(",", ".")
            current_range = f"{start} - {end}"
            continue
        if not is_vtt and line.isdigit() and current_range is None:
            continue
        cue_lines.append(line)
    _flush()

    full_text = "\n".join(seg.text for seg in segments).strip()
    return ExtractionResult(full_text=full_text, segments=segments)


def extract_document_text(extension: str, raw_bytes: bytes) -> ExtractionResult:
    """Dispatch text extraction by validated file extension."""
    ext = extension.lower()
    if ext == ".pdf":
        result = _extract_pdf(raw_bytes)
    elif ext == ".docx":
        result = _extract_docx(raw_bytes)
    elif ext == ".md":
        result = _extract_markdown(raw_bytes)
    elif ext in {".html", ".htm"}:
        result = _extract_html(raw_bytes)
    elif ext == ".txt":
        result = _extract_plain_text(raw_bytes)
    elif ext == ".vtt":
        result = _extract_transcript(raw_bytes, is_vtt=True)
    elif ext == ".srt":
        result = _extract_transcript(raw_bytes, is_vtt=False)
    else:
        raise ValidationError(f"Unsupported extension '{ext}'.", code="unsupported_file_type")

    if not result.full_text.strip():
        raise ValidationError(
            "No readable text could be extracted from the uploaded file.",
            code="empty_extracted_text",
        )
    return result
