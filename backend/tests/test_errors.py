from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.error_handlers import register_exception_handlers
from app.core.exceptions import AppError
from app.core.middleware import register_request_middleware


def make_test_app() -> FastAPI:
    test_app = FastAPI()
    register_request_middleware(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/validation/{item_id}")
    def validation_route(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @test_app.get("/failure")
    def failure_route() -> None:
        raise RuntimeError("internal detail must not be exposed")

    @test_app.get("/bad-request")
    def bad_request_route() -> None:
        raise AppError(message="invalid operation", code="INVALID_OPERATION")

    return test_app


def test_not_found_uses_standard_error_shape() -> None:
    response = TestClient(make_test_app()).get("/missing")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "HTTP_404"
    assert response.json()["error"]["request_id"]


def test_bad_request_uses_application_error_code() -> None:
    response = TestClient(make_test_app()).get("/bad-request")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OPERATION"


def test_validation_error_does_not_expose_traceback() -> None:
    response = TestClient(make_test_app()).get("/validation/not-an-integer")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "traceback" not in response.text.lower()


def test_unhandled_error_is_logged_but_hidden_from_client() -> None:
    response = TestClient(make_test_app(), raise_server_exceptions=False).get("/failure")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "internal detail" not in response.text
