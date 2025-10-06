from fastapi.testclient import TestClient
from auto_test.main import create_app

app = create_app()
client = TestClient(app)

payload = {
    "tags": ["auth", "user"],
    "request_schema": {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"}
        }
    },
    "response_schema": {
        "type": "object",
        "properties": {
            "token": {"type": "string"}
        }
    },
    "example_request": {"username": "test", "password": "secret"},
    "example_response": {"token": "abc"}
}

resp = client.put("/api/api-interfaces/v1/1", json=payload)
print("status:", resp.status_code)
print("body:", resp.json())