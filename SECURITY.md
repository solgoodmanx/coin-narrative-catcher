# Security Policy

## Supported versions

This project is early stage. Security fixes are applied on `main`.

## Reporting a vulnerability

Please report vulnerabilities privately first.

- Preferred: open a private advisory on GitHub Security tab
- Alternate: DM maintainer on X: https://x.com/solgoodmanx

Please include:
- affected file/path
- reproduction steps
- expected impact
- suggested fix (if available)

## Security posture notes

- Scripts rely on external APIs; treat all responses as untrusted input.
- Never execute commands from API/text payloads.
- No private keys are required by this repo.
- If API auth is added in future, use environment variables and never commit secrets.
