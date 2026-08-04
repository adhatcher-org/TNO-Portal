"""Security-focused redirect tests."""

from __future__ import annotations

from tests.test_app import extract_csrf_token


def test_language_preference_rejects_untrusted_return_paths(client) -> None:
    page = client.get("/")
    csrf_token = extract_csrf_token(page.get_data(as_text=True))

    for next_path in (
        "https://attacker.example/path",
        "//attacker.example/path",
        "/\\\\attacker.example/path",
        "https:/attacker.example/path",
        "https:///attacker.example/path",
        "/login?next=/accounts",
        "/#fragment",
        "/does-not-exist",
        "not-a-path",
        "",
    ):
        response = client.post(
            "/preferences/language",
            data={"language": "fr", "csrf_token": csrf_token, "next_path": next_path},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/"


def test_language_preference_allows_known_return_paths(client) -> None:
    page = client.get("/")
    csrf_token = extract_csrf_token(page.get_data(as_text=True))

    for next_path in ("/", "/login", "/create-account-access", "/create-account", "/user-info", "/accounts"):
        response = client.post(
            "/preferences/language",
            data={"language": "fr", "csrf_token": csrf_token, "next_path": next_path},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == next_path


def test_language_preference_cookie_uses_allowlisted_language_values(client) -> None:
    page = client.get("/")
    csrf_token = extract_csrf_token(page.get_data(as_text=True))

    response = client.post(
        "/preferences/language",
        data={
            "language": "fr\r\nSet-Cookie: attacker=1",
            "csrf_token": csrf_token,
            "next_path": "/",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["language"] == "en"
