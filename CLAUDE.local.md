# CLAUDE.local.md — personal preferences (not committed)

## Style
- Responses in French, code and comments in English
- Prefer concise explanations, no verbose recaps
- When proposing changes, always show a diff or the minimal modified block

## Workflow preferences
- Always run in Plan mode for changes touching `services/`, `models/`, or `migrations/`
- Before touching `deployment_service.py`, read `agent_docs/deployment_flow.md`
- Prefer explicit error messages with context (service name, operation, entity id)

## Local environment
- OS: Linux
- Editor: VSCode + Neovim keybindings
- Python managed via uv (no system Python)
- `.env` file present at `api/.env` — never read or log its contents
