# Local validation

Validated on 2026-09-15 using Python 3.14 on Windows.

- 4 automated tests passed with `python -m pytest -q`.
- `python demo.py` successfully exercised the local API and produced `demo-output.json`.
- Actual output screenshot: `demo.png` (rendered from captured JSON, not a model-generated image).
- Database fixtures are isolated from application data.
- Third-party Starlette/AnyIO emits a deprecation warning; no test failures.
- Docker is unavailable locally; container execution is not claimed.

See README limitations for optional integrations and unverified real-world model quality.

MCP protocol verification: started the real stdio server, initialized a client, discovered the three expected tools, called business_report and verified an invalid plan returns a tool error.
