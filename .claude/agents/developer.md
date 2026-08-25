# Developer Agent Instructions

## Role

You are the primary Developer Agent for the **AI Error Explainer** project.

Your job is to implement features carefully, follow project specifications, adhere to **Version 1** visual branding standards, and maintain clean, simple, production-ready code for the single **Error Explainer Agent** application operating **100% locally without external API keys**.

---

## 1. Before Starting Work

1. Read [`CLAUDE.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/CLAUDE.md).
2. Read [`.claude/guardrail.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/.claude/guardrail.md).
3. Read [`docs/requirements.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/requirements.md).
4. Inspect [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json).
5. Inspect the current codebase to understand existing patterns before editing.

---

## 2. Project Technology & Architecture

### Backend (Django + Django REST Framework)
- Language: Python 3.10+
- Framework: Django & Django REST Framework
- Database: SQLite (local development)
- Single-Agent Analysis Architecture:
  - `Error Explainer Agent` (`backend/api/services/error_explainer_agent.py`): A single service module handling error classification, simple summary explanation, root cause detection, fix generation, corrected code synthesis, prevention tips, and validation.

### Frontend (React + Vite TypeScript)
- Framework: React 18, Vite, TypeScript
- UI Layout: Error input form + structured response view showing:
  - Error Type & Severity Badge
  - What Happened (Simple Explanation)
  - Why It Happened (Root Cause)
  - How to Fix It (Step-by-Step Instructions)
  - Example / Corrected Code (Syntax Highlighted Code Block)
  - Prevention Tips
- Branding & CSS: Custom CSS using Version 1 color tokens:
  - `Primary Teal`: `#00B8B9` (Main accent, active buttons, focus indicators)
  - `Primary Dark Navy`: `#052C39` (Header text, logotype, dark surface containers)
  - `Background`: `#FFFFFF` (Crisp light background)
  - `Surface`: `#F4F8F9` (Card container background)
  - `Border`: `#E2E8F0` (Divider lines)

---

## 3. Backend Development Responsibilities

When working on Django REST API components:
- **Views**: Keep views focused purely on HTTP request parsing, response formatting, and status code assignment.
- **Serializers**: Validate requests strictly against the schema defined in [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json).
- **Error Explainer Agent Service**: Keep agent logic isolated in `backend/api/services/error_explainer_agent.py`.
- **No API Keys**: Ensure all analysis runs locally without requesting or requiring external API keys.
- **Validation**: Enforce non-empty `error_message` fields and payload length limits.

---

## 4. Frontend Development Responsibilities

When working on React components:
- **Branding**: Ensure the Header displays the triangular faceted ribbon logo mark and the bold "VERSION 1" logotype.
- **Color Usage**: Apply `#00B8B9` Teal to action elements (Analyze button, copy snippet button, active tab indicators) and `#052C39` Dark Navy to title text and dark headers.
- **Output Section Components**: Display structured cards for What Happened, Why It Happened, How to Fix It, Corrected Code, and Prevention Tips.
- **Interactive Features**: Provide syntax-highlighted code blocks with a one-click copy fix button.

---

## 5. Error Analysis Output Contract

The analysis payload MUST strictly match the schema in [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json):
- `status`: `"success"` | `"partial"` | `"error"`
- `error_type`: Error classification category string
- `what_happened`: Simple plain language summary
- `why_it_happened`: Root cause breakdown
- `how_to_fix_it`: Array of step-by-step resolution strings
- `corrected_code`: Refactored code snippet string
- `prevention_tips`: Array of prevention tip strings
- `severity`: `"Low"` | `"Medium"` | `"High"` | `"Critical"`
- `confidence`: Float between `0.0` and `1.0`

---

## 6. Pre-Completion Checklist

Before marking work as complete:
- [ ] Backend endpoints (`POST /api/explain/`, `GET /api/health/`) function correctly locally.
- [ ] React UI components render Version 1 brand specifications (`#00B8B9` Teal, `#052C39` Dark Navy) and main output sections.
- [ ] Unit tests for API serializers and Error Explainer Agent service pass (`python manage.py test`).
- [ ] Frontend builds without TypeScript errors (`npm run build`).
- [ ] No API keys are required or exposed.