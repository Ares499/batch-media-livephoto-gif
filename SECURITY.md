# Security Notes

This repository is intended for public portfolio use.

## What is intentionally excluded

- Local input media files.
- Generated GIF, Live Photo, video, or image outputs.
- `.DS_Store`, caches, logs, virtual environments, and local-only files.
- API keys, accounts, tokens, cookies, credentials, or private configuration.

## Safe usage

- Review media files before publishing generated outputs.
- Do not commit client files, unreleased content, or copyrighted material unless you have the right to share it.
- Keep generated outputs in `output/`; this folder is ignored by Git.

## Scope

This is a local batch-processing tool. It does not run a server, expose network ports, or require remote credentials.
