# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest `master` | ✅ |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Report vulnerabilities privately via GitHub Security Advisories:
https://github.com/roblitz-spec/RuleForge/security/advisories/new

You can expect:

- **Acknowledgement** within 48 hours
- **Status update** within 5 business days
- **Resolution timeline** based on severity

## Scope

Security considerations for RuleForge include:

- Rule execution safety (prevent unintended filesystem operations)
- Input validation and sanitization in rule parameters
- Safe handling of file paths and metadata
- Desktop application security (PySide6)

## Disclosure

We follow coordinated disclosure. After a fix is released, we will publish
a security advisory crediting the reporter (unless anonymity is requested).
