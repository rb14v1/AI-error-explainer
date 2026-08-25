# Agent Specification: AI Error Explainer

## 1. System Overview

### Project Name
**AI Error Explainer System**

### Purpose
The **AI Error Explainer** is a developer assistant designed to help developers quickly understand, debug, and fix programming errors using **Claude Code**, Django REST Framework, and React + Vite.

The system features a single **Error Explainer Agent** (`backend/api/services/error_explainer_agent.py`) that processes developer error payloads (error message, stack trace, code snippet, language context) completely locally without external API keys.

It classifies the root issue, explains what happened in simple terms, determines why it occurred, generates step-by-step resolution steps, provides corrected code examples, and offers prevention tips.

The application UI is styled following the official **Version 1** visual brand standards (`#00B8B9` Teal accent and `#052C39` Dark Slate Navy).

---

## 2. Agent Specification: Error Explainer Agent

The **Error Explainer Agent** is the core analysis engine of the application:

```text
               ┌──────────────────────────────────────┐
               │    Developer Error Input Submission  │
               │ (Message, Stack Trace, Code, Lang)   │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │         Django REST API View         │
               │   (Input Validation & Sanitization)  │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │        Error Explainer Agent         │
               │  - Classification & Taxonomy         │
               │  - What Happened (Simple Language)   │
               │  - Why It Happened (Root Cause)      │
               │  - How to Fix It (Step-by-Step)      │
               │  - Corrected Example Code Snippet    │
               │  - Prevention Tips                   │
               │  - Severity & Confidence Evaluation  │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │  Version 1 Branded UI Response View  │
               │  (Header Logo + Teal/Navy Theme)     │
               └──────────────────────────────────────┘
```

### Agent Internal Responsibilities:

1. **Error Classification**: Parses error string, extracts error type (e.g. `SyntaxError`, `TypeError`, `NullPointer`, `DoesNotExist`), and assigns `severity` (`Low`/`Medium`/`High`/`Critical`) and `confidence` (`0.0`-`1.0`).
2. **What Happened Explanation**: Synthesizes a plain language, jargon-free summary explaining the error.
3. **Root Cause Analysis**: Analyzes stack trace frames and surrounding context to explain `why_it_happened`.
4. **Fix Generation**: Produces actionable step-by-step `how_to_fix_it` instructions.
5. **Code Refactoring**: Generates a clean, refactored `corrected_code` example snippet.
6. **Prevention Tips**: Formulates actionable best practice `prevention_tips`.
7. **Validation**: Ensures schema compliance and code safety.

---

## 3. Data Contract & JSON Schema

All requests and responses MUST conform to [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json).

### Response Schema Specification:
```json
{
  "status": "success",
  "error_type": "TypeError / Undefined Access",
  "what_happened": "The code tried to loop over 'users' using .map(), but 'users' had no value (undefined) when the function ran.",
  "why_it_happened": "The parent component called UserList without passing the 'users' prop, or the data fetch request had not completed yet.",
  "how_to_fix_it": [
    "Define a default empty array parameter for users (users = []).",
    "Use optional chaining (users?.map(...)) before calling array methods.",
    "Add a loading check in the parent component before rendering UserList."
  ],
  "corrected_code": "const UserList = ({ users = [] }: { users?: Array<{ id: string; name: string }> }) => {\n  return <div>{users?.map(u => <p key={u.id}>{u.name}</p>)}</div>;\n};",
  "prevention_tips": [
    "Enable strictNullChecks in tsconfig.json.",
    "Use TypeScript interface default props or fallbacks for all array components."
  ],
  "severity": "High",
  "confidence": 0.95
}
```

---

## 4. Security & Guardrail Standards

- **Zero Code Execution**: Submitted code snippets are analyzed via static rules — NEVER executed.
- **No External API Key Dependencies**: Runs 100% locally without calling external cloud AI APIs.
- **Prompt Injection Defense**: Error strings are handled as pure literal string data.
- **Guardrails**: Complies with [`.claude/guardrail.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/.claude/guardrail.md).

---

## 5. Definition of Done

The system implementation is complete when:
- [ ] Endpoints `POST /api/explain/` and `GET /api/health/` match [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json).
- [ ] Single Error Explainer Agent (`backend/api/services/error_explainer_agent.py`) is implemented and verified.
- [ ] React UI displays the Version 1 logo mark, "VERSION 1" logotype, Teal (`#00B8B9`), and Dark Navy (`#052C39`) theme.
- [ ] Backend tests verify local Error Explainer Agent payload validation and error handling.
- [ ] Documentation (`README.md`, `CLAUDE.md`, `docs/requirements.md`, `.claude/guardrail.md`) matches codebase specifications.
