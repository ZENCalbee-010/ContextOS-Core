# Security Policy

## Supported Versions

ContextOS Core is early-stage local-first software. Security fixes target the latest development branch unless a release branch is explicitly maintained.

## Reporting a Vulnerability

Please do not open a public issue for sensitive security reports.

Report vulnerabilities privately through GitHub Security Advisories if available for the repository. If advisories are not available, contact the maintainers through a private channel and include:

- A short description of the issue
- Steps to reproduce
- Impact and affected files
- Any suggested mitigation

## Security Model

ContextOS Core is designed as a local single-user CLI application.

Important boundaries:

- Imported files are stored locally in SQLite.
- API keys must come from environment variables.
- Dry-run and mock adapter workflows must not call external AI services.
- The project does not include a web server, hosted API, multi-user auth, or cloud sync.

## Sensitive Data

Users should avoid importing secrets, private credentials, or confidential documents unless they intend to store that content in the local SQLite database.

Debug output should not expose API key values. If a future patch adds live AI calls or richer logging, it must include secret redaction tests.
