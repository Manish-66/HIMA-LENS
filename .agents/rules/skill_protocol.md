## Mandatory Pre-Task Skill Protocol

Before generating any response or executing code changes:
1. Review all available skills in `.agents/skills/`.
2. Activate and strictly follow the skill required by the task:
   - **Voice & conciseness**: `caveman` (answer first, zero fluff, terse smart caveman voice).
   - **Minimal change & scope discipline**: `ponytail` (smallest working diff, end with skipped/risk).
   - **Codebase structure & relationships**: `graphify` (query graph first, run `graphify update .` after code edits).
   - **UI / Design / Print / CSS / Heuristics**: `impeccable` (consult craft floor, run `impeccable detect`).
   - **Security / Auth / Endpoints / Vulnerabilities**: `security-auditor` (proactive OWASP checks).
   - **Domain entities / Definitions**: `domain-modeling` (strict terminology boundaries against glossary).
   - **Requirements discovery & Clarification**: `grilling` (structured decision tree rounds with recommended answers).
   - **Architectural visuals & control flow**: `show-me` (Mermaid, component trees, diffs).
3. Read the target `SKILL.md` before proceeding whenever executing a task in that domain.
