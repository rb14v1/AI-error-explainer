# Requirements Specification: AI Error Explainer

## 1. System Overview

The **AI Error Explainer** is a developer assistant built using **Claude Code**, Django REST Framework, and React + Vite. The system takes developer-submitted programming errors, stack traces, code snippets, and optional language context, processes them through a single **Error Explainer Agent**, and returns structured explanations, root cause analyses, step-by-step solutions, corrected code examples, and prevention tips.

The application operates completely locally using a local deterministic Error Explainer Agent and requires **no external AI API keys**.

The application UI is branded using the official **Version 1** visual identity (triangular faceted ribbon logo mark, `#00B8B9` Teal accent, and `#052C39` Dark Slate Navy headers).

---

## 2. Key Objectives

- **Automate Error Diagnosis**: Provide developers with fast, accurate explanations of why code failed using the Error Explainer Agent.
- **Actionable Fixes & Prevention**: Generate step-by-step solutions, corrected code snippets, and prevention tips.
- **Single-Agent Architecture**: Use one specialized **Error Explainer Agent** (`backend/api/services/error_explainer_agent.py`) to handle classification, explanation, root cause analysis, fix generation, and validation.
- **Offline & Local Analysis Engine**: Perform error classification and reasoning locally without requiring external API keys.
- **Version 1 Visual Standards**: Deliver a high-contrast, professional, branded developer UI using Version 1 color tokens (`#00B8B9` Teal, `#052C39` Dark Navy).
- **Safety & Security**: Ensure untrusted user inputs never execute on the host server.

---

## 3. Functional Requirements

### FR-01 — Error Submission
The system shall provide a web input interface allowing developers to submit:
- `error_message` (Required string)
- `stack_trace` (Optional string)
- `code_snippet` (Optional string)
- `language` (Optional programming language string, e.g., TypeScript, Python, Java)

### FR-02 — Input Validation & Sanitization
The system shall validate request payloads against the JSON schema specified in [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json):
- Reject empty error messages with a `400 Bad Request`.
- Limit payload sizes to prevent memory exhaustion (e.g. max 50KB).
- Sanitize inputs to prevent XSS or prompt injection exploits.

### FR-03 — Error Explainer Agent Analysis Flow
The single **Error Explainer Agent** shall process submitted payloads through an integrated 7-step analysis workflow:
1. **Classification**: Identify `error_type` category and evaluate `severity` & `confidence`.
2. **Simple Explanation**: Explain `what_happened` in clear, jargon-free developer language.
3. **Root Cause Analysis**: Analyze stack frames and code context to explain `why_it_happened`.
4. **How to Fix It**: Generate step-by-step `how_to_fix_it` resolution actions.
5. **Corrected Code**: Produce a refactored/corrected `corrected_code` snippet.
6. **Prevention Tips**: Provide actionable `prevention_tips` to avoid future recurrence.
7. **Validation & Quality Check**: Ensure safety and schema compliance.

### FR-04 — Structured Response Payload Contract
The response MUST contain all key output sections:
- **Error Type** (`error_type`): Category / taxonomy.
- **What Happened** (`what_happened`): Simple plain language summary.
- **Why It Happened** (`why_it_happened`): Root cause breakdown.
- **How to Fix It** (`how_to_fix_it`): Step-by-step resolution array.
- **Example / Corrected Code** (`corrected_code`): Working refactored code.
- **Prevention Tips** (`prevention_tips`): Actionable tips to avoid recurrence.
- **Severity & Confidence**: Rating (`Low`/`Medium`/`High`/`Critical`) and score (`0.0`-`1.0`).

### FR-05 — Version 1 Branded UI Interface
The React frontend UI shall incorporate the official **Version 1** visual identity:
- **Header**: Displays the triangular faceted ribbon logo mark alongside the bold "VERSION 1" logotype.
- **Color Scheme**:
  - Primary Teal Accent (`#00B8B9`) for primary submission buttons, active tabs, copy buttons, and highlights.
  - Primary Dark Navy (`#052C39`) for header typography, dark card containers, and titles.
  - Light mode crisp background (`#FFFFFF`) with `#F4F8F9` container surfaces.
- **Output Display**: Syntax-highlighted code blocks with "Copy Code" button, clear severity badges, and structured sections for What Happened, Why It Happened, How to Fix It, and Prevention Tips.

### FR-06 — API & Schema Compliance
The backend API shall strictly implement the REST endpoints described in [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json):
- `POST /api/explain/` — Error analysis endpoint.
- `GET /api/health/` — Health check endpoint.

---

## 4. Safety & Security Requirements

### SR-01 — Zero Execution Policy
User-provided error messages, stack traces, and code snippets shall be treated as **pure untrusted text data**. The backend shall NEVER execute, evaluate (`eval()`), or run commands from user input.

### SR-02 — No External API Dependencies
The application shall operate locally without requiring third-party API keys or external cloud model service credentials.

### SR-03 — Defensive Prompt Handling
Text inside user error payloads that resembles system instructions or prompt injection attempts must be treated purely as literal string data.

---

## 5. Non-Functional Requirements

- **NFR-01 — Modularity**: Clean separation of concerns between React UI, Django REST API views, and Error Explainer Agent service module.
- **NFR-02 — Performance**: Fast local response times (< 1 second response time).
- **NFR-03 — Reliability**: 100% offline availability with zero reliance on external network APIs.
- **NFR-04 — Usability**: Developer-centric design formatted with clear typography and Version 1 brand styling.

---

## 6. Technical Stack Requirements

- **Backend Framework**: Python, Django REST Framework
- **Frontend Framework**: React, Vite, TypeScript
- **Analysis Architecture**: Single Error Explainer Agent (No API keys required)
- **API Spec**: JSON Schema (`docs/api_schema.json`)
- **Version Control**: Git
