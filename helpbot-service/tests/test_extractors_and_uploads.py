"""Tests for upload validation and 7-format baseline text extraction."""

from __future__ import annotations

import io
from pathlib import Path

from docx import Document as DocxDocument
from fastapi.testclient import TestClient

from app.utilities.text_extractors import extract_document_text

FIXTURES_DIR = Path(__file__).parent / "fixtures"

DEV_HEADERS = {
    "X-HelpBot-Tenant-Id": "campusdesk-dev",
    "X-HelpBot-User-Id": "adv-elena-navarro",
    "X-HelpBot-User-Role": "advisor",
}


def _make_sample_docx_bytes() -> bytes:
    doc = DocxDocument()
    doc.add_heading("Academic Advising Guidelines", level=1)
    doc.add_paragraph("Students should meet their advisor once per semester before registration.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_minimal_pdf_bytes() -> bytes:
    # Minimal valid single-page PDF containing readable text stream.
    return (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length 55 >> stream\n"
        b"BT /F1 12 Tf 20 80 Td (CampusDesk Exam Policy Guide) Tj ET\n"
        b"endstream endobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000241 00000 n \n"
        b"0000000346 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n416\n%%EOF\n"
    )


def test_text_extractors_for_all_supported_formats() -> None:
    md_res = extract_document_text(".md", (FIXTURES_DIR / "course_registration_policy.md").read_bytes())
    assert "18 credits" in md_res.full_text
    assert any(seg.page_or_section == "Add/Drop Deadlines" for seg in md_res.segments)

    txt_res = extract_document_text(".txt", (FIXTURES_DIR / "library_borrowing_guide.txt").read_bytes())
    assert "21 calendar days" in txt_res.full_text

    html_res = extract_document_text(".html", (FIXTURES_DIR / "examination_handbook.html").read_bytes())
    assert "72 hours" in html_res.full_text
    assert any(seg.page_or_section == "Medical Makeup Examinations" for seg in html_res.segments)

    vtt_res = extract_document_text(".vtt", (FIXTURES_DIR / "fee_schedule_overview.vtt").read_bytes())
    assert "September 15" in vtt_res.full_text
    assert vtt_res.segments[0].timestamp_range == "00:00:02.000 - 00:00:09.500"

    srt_res = extract_document_text(".srt", (FIXTURES_DIR / "campus_facilities_walkthrough.srt").read_bytes())
    assert "study pod" in srt_res.full_text.lower()
    assert srt_res.segments[0].timestamp_range == "00:00:01.000 - 00:00:07.500"

    docx_res = extract_document_text(".docx", _make_sample_docx_bytes())
    assert "meet their advisor" in docx_res.full_text
    assert any(seg.page_or_section == "Academic Advising Guidelines" for seg in docx_res.segments)

    pdf_res = extract_document_text(".pdf", _make_minimal_pdf_bytes())
    assert "CampusDesk Exam Policy Guide" in pdf_res.full_text
    assert pdf_res.segments[0].page_or_section == "Page 1"


def test_upload_list_and_delete_document(client: TestClient) -> None:
    md_bytes = (FIXTURES_DIR / "course_registration_policy.md").read_bytes()
    upload_resp = client.post(
        "/api/knowledge/documents",
        headers=DEV_HEADERS,
        data={
            "application_id": "campusdesk",
            "module_id": "course-registration",
            "screen_id": "registration-overview",
            "title": "Course Registration Policy",
        },
        files={"file": ("../nested/course_registration_policy.md", md_bytes, "text/markdown")},
    )
    assert upload_resp.status_code == 201
    doc = upload_resp.json()
    assert doc["original_filename"] == "course_registration_policy.md"
    assert doc["file_type"] == "md"
    assert doc["character_count"] > 50

    list_resp = client.get("/api/knowledge/documents", headers=DEV_HEADERS)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    del_resp = client.delete(f"/api/knowledge/documents/{doc['id']}", headers=DEV_HEADERS)
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True


def test_unsupported_file_extension_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/knowledge/documents",
        headers=DEV_HEADERS,
        files={"file": ("screenshot.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "unsupported_file_type"
