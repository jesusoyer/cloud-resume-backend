"""Smoke tests: run AFTER deploy, against the real, live API.

The workflow passes the API address in the API_URL environment variable.
Without it (e.g. running pytest on your laptop), these tests are skipped.
"""
import json
import os
import urllib.error
import urllib.request

import pytest

API_URL = os.environ.get("API_URL")
ORIGIN = "https://resume.jesoyer.com"

pytestmark = pytest.mark.skipif(not API_URL, reason="API_URL not set; smoke tests run after deploy")


def post():
    request = urllib.request.Request(API_URL, method="POST", headers={"Origin": ORIGIN})
    with urllib.request.urlopen(request, timeout=10) as response:
        headers = {k.lower(): v for k, v in response.headers.items()}
        return response.status, headers, json.loads(response.read())


def test_returns_a_count():
    status, _, body = post()
    assert status == 200
    assert isinstance(body["count"], int)
    assert body["count"] >= 1


def test_count_goes_up():
    _, _, first = post()
    _, _, second = post()
    assert second["count"] > first["count"]   # real visitors may add more, so ">" not "== +1"


def test_cors_allows_resume_site():
    _, headers, _ = post()
    assert headers.get("access-control-allow-origin") == ORIGIN


def test_get_is_rejected():
    # Only POST /count exists; a GET must not count a visit
    request = urllib.request.Request(API_URL, method="GET")
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(request, timeout=10)
    assert error.value.code in (403, 404, 405)