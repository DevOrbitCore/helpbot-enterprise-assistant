"""Tests for baseline keyword retrieval, no-evidence guard, and tenant/user isolation."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.services.chat_service import NO_EVIDENCE_RESPONSE

FIXTURES_DIR = Path(__file__).parent / "fixtures"

USER_A_HEADERS = {
    "X-HelpBot-Tenant-Id": "campusdesk-dev",
    "X-HelpBot-User-Id": "stu-maya-chen",
    "X-HelpBot-User-Role": "student",
}

USER_B_HEADERS = {
    "X-HelpBot-Tenant-Id": "campusdesk-dev",
    "X-HelpBot-User-Id": "ta-rohan-kulkarni",
    "X-HelpBot-User-Role": "ta",
}

OTHER_TENANT_HEADERS = {
    "X-HelpBot-Tenant-Id": "other-university",
    "X-HelpBot-User-Id": "stu-maya-chen",
    "X-HelpBot-User-Role": "student",
}


def test_no_evidence_returns_clear_guard_message(client: TestClient) -> None:
    resp = client.post(
        "/api/chat",
        headers=USER_A_HEADERS,
        json={
            "message": "What is the campus shuttle schedule to the airport?",
            "context": {
                "tenant_id": "campusdesk-dev",
                "application_id": "campusdesk",
                "user_id": "stu-maya-chen",
                "role": "student",
                "module_id": "campus-facilities",
                "screen_id": "facility-booking",
                "route": "/facilities",
                "page_title": "Campus Facilities",
                "locale": "en-US",
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grounded"] is False
    assert data["sources"] == []
    assert data["assistant_message"]["content"] == NO_EVIDENCE_RESPONSE


def test_keyword_retrieval_grounding_and_tenant_isolation(client: TestClient) -> None:
    # Upload library guide under campusdesk-dev tenant
    txt_bytes = (FIXTURES_DIR / "library_borrowing_guide.txt").read_bytes()
    upload = client.post(
        "/api/knowledge/documents",
        headers=USER_A_HEADERS,
        data={
            "application_id": "campusdesk",
            "module_id": "library-services",
            "screen_id": "borrowing-rules",
            "title": "Campus Library Borrowing Guide",
        },
        files={"file": ("library_borrowing_guide.txt", txt_bytes, "text/plain")},
    )
    assert upload.status_code == 201

    # User A in same tenant gets grounded answer with structured source metadata
    chat_resp = client.post(
        "/api/chat",
        headers=USER_A_HEADERS,
        json={
            "message": "How many days is the undergraduate library loan period and overdue fine?",
            "context": {
                "tenant_id": "campusdesk-dev",
                "application_id": "campusdesk",
                "user_id": "stu-maya-chen",
                "role": "student",
                "module_id": "library-services",
                "screen_id": "borrowing-rules",
                "route": "/library",
                "page_title": "Library Services",
                "locale": "en-US",
            },
        },
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["grounded"] is True
    assert len(chat_data["sources"]) == 1
    source = chat_data["sources"][0]
    assert source["file_name"] == "library_borrowing_guide.txt"
    assert source["module_id"] == "library-services"
    assert "21 calendar days" in chat_data["assistant_message"]["content"]

    conv_id = chat_data["conversation_id"]

    # User A can read their own conversation
    own_conv = client.get(f"/api/conversations/{conv_id}", headers=USER_A_HEADERS)
    assert own_conv.status_code == 200
    assert len(own_conv.json()["messages"]) == 2

    # User B in same tenant CANNOT access or delete User A's conversation by ID
    cross_user = client.get(f"/api/conversations/{conv_id}", headers=USER_B_HEADERS)
    assert cross_user.status_code == 404
    cross_delete = client.delete(f"/api/conversations/{conv_id}", headers=USER_B_HEADERS)
    assert cross_delete.status_code == 404

    # Different tenant cannot retrieve campusdesk-dev documents
    other_tenant_chat = client.post(
        "/api/chat",
        headers=OTHER_TENANT_HEADERS,
        json={
            "message": "What is the undergraduate library loan period?",
            "context": {
                "tenant_id": "other-university",
                "application_id": "campusdesk",
                "user_id": "stu-maya-chen",
                "role": "student",
                "module_id": "library-services",
                "screen_id": "borrowing-rules",
                "route": "/library",
                "page_title": "Library Services",
                "locale": "en-US",
            },
        },
    )
    assert other_tenant_chat.status_code == 200
    assert other_tenant_chat.json()["grounded"] is False
    assert other_tenant_chat.json()["sources"] == []
