# Backend Changelog - Response Schema Compatibility (2025-09-29)

## Summary

Implement unified response parameters for API Interface Management:

- Prioritize `response_schema` in service layer responses
- Fallback to `example_response` when `response_schema` is empty or absent
- Parse JSON strings to objects for both fields to ensure consistent structure returned to frontend

## Files Updated

- backend/src/auto_test/services/api_interface_service.py
  - Method `_apply_business_rules`: normalize `request_schema` and `response_schema`
  - Request: prefer `request_schema`, fallback to legacy `request_params`
  - Response: prefer `response_schema`, fallback to `example_response`

## Database Schema (No change required)

Table `api_interfaces` includes both columns:

- `response_schema` TEXT
- `example_response` TEXT

The service layer now guarantees a non-empty `response_schema` in the API payload by converting `example_response` when `response_schema` is missing.

## Affected Endpoints

- GET /api/api-interfaces/v1/
- GET /api/api-interfaces/v1/{id}

Both endpoints now return `response_schema` populated either from stored schema or converted example.

## Testing

1. Start backend: `python backend/start_api_v2.py --port 8000`
2. Verify list response:
   - `curl -s http://localhost:8000/api/api-interfaces/v1/`
   - Ensure items contain `response_schema` object
3. Verify detail response:
   - `curl -s http://localhost:8000/api/api-interfaces/v1/{id}`
   - Confirm `response_schema` is present and parsed

## Frontend Alignment

Frontend components use `response_schema` first and fallback to `example_response` via `ParamsConverter`:

- Page Management: `PageApiConfig.vue` adds "响应字段参考" panel
- Workflow Orchestration: `ApiCallNode.vue` adds "响应字段参考" panel

This changelog documents the backend side ensuring these panels receive consistent data.