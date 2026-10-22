# MANDATORY PRE-RESPONSE SKILL RESOLUTION PROTOCOL (HARD INVARIANT)

## Absolute Invariant
Before generating ANY user-facing text, making code changes, or calling final tools, you MUST evaluate the active skill requirements. A turn that bypasses relevant skills is a failed turn.

---

## 1. Step 0: Pre-Task Skill Resolution Gate
On EVERY turn, execute this internal 3-step gate before any action:
1. **Identify the Domain**: Parse the user's intent into one or more domains (Architecture, UI/Design, Code change, Security/Auth, Domain Concepts, Architecture Visuals, Planning/Decisions).
2. **Match Relevant Skills**: Check the active skills list in `.agents/skills/`.
3. **Read & Execute Skill Contract**: Read the specific `SKILL.md` file from `.agents/skills/<skill>/SKILL.md` and adhere strictly to its operational rules.

---

## 2. Skill Trigger & Execution Matrix

| Domain / Intent | Required Skill | Pre-Execution Command / Protocol | Mandatory Output Invariants |
|---|---|---|---|
| **Codebase query, file relationships, or architecture exploration** | `graphify` | First run `graphify query "<question>"` (CLI) before reading raw files. Run `graphify update .` immediately after modifying code files. | Answer using the scoped subgraph from `graphify-out/graph.json`. |
| **Frontend UI, CSS, layout, typography, components, print, responsive design** | `impeccable` | 1. Respect existing project tokens (`--forest`, `--paper`, `--ink`, `--line`). Never change theme unless explicitly asked.<br>2. Run `craft-floor` checks.<br>3. Run `.agents/skills/impeccable/scripts/impeccable.cmd detect --json <targets>` on every modified template to eliminate low-contrast, nested cards, and broken images. | Production-grade code, zero WCAG contrast failures, no ghost cards (declare border OR shadow, never both). |
| **Code implementation, bug fix, refactor, dependency choice** | `ponytail` | Seek the smallest complete change that fully solves the problem. Use existing patterns and standard library first; zero bloat, zero unnecessary wrappers. | **MANDATORY CLOSING**: End your reply with 1–2 lines stating what was skipped/not checked and any critical risk the user must know. |
| **Endpoints, APIs, Auth, Data Storage, User Input, Permissions** | `security-auditor` | Proactively audit OWASP Top 10: Broken Access Control (auth checks on `/admin` and `/api/*`), Injection, Missing Rate Limits, and Data Exposure. | Call out security vulnerabilities immediately with concrete remediation steps. |
| **Domain entities, naming, schema definitions, business logic boundaries** | `domain-modeling` | Validate terms against domain glossary. Challenge overloaded or ambiguous vocabulary immediately (e.g. Incident vs Assessment vs Advisory vs CAP Alert). | Maintain strict domain separation devoid of low-level implementation details. |
| **Ambiguous requirements, architectural forks, planning decisions** | `grilling` | Map the problem into a design tree frontier. Organize questions in numbered decision rounds. | Format every question as:<br>`❓ **Q<n>** - **<title>**: <body/choices>`<br>`➡️ <recommended answer>`<br>(Worded so "yes" accepts recommendation). |
| **Visualizing architecture, runtime flow, component trees, or diffs** | `show-me` | Pick the smallest visual view that clarifies the concept: Mermaid sequence/flowcharts, component trees, or targeted diffs. | Skip wordy preambles; let the diagram or component tree speak directly. |
| **Conversational tone and communication style** | `caveman` | Permanent session voice: answer first, fluff dead, every technical fact kept. No greetings ("Sure!", "Hello"), no hedging, no empty recaps, no pleasantries. | Terse, active voice, under 20 words per sentence where possible. Payload (paths, commands, code) verbatim. |

---

## 3. Pre-Send Compliance Filter
Before sending your response, verify:
* [ ] Did I query `graphify` if this was a codebase question?
* [ ] Did I run `impeccable detect` if templates/UI were edited?
* [ ] Did I apply `caveman` voice (answer first, zero fluff)?
* [ ] Did I end with `ponytail` skipped/risk lines?
* [ ] If asking clarifying questions, did I format them with `grilling` (`❓ Q` / `➡️ Recommendation`)?
