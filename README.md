# AI Error Explainer

An AI-powered developer tool that analyzes programming errors, stack traces, and code snippets using a single **Error Explainer Agent**. It classifies the error, explains what happened in simple terms, identifies the root cause, provides step-by-step resolution instructions, generates corrected example code, and offers prevention tips.

Built using **Claude Code**, Django REST Framework, and React + Vite, styled according to the official **Version 1** visual identity.

> [!NOTE]
> **Zero External API Keys**: This project operates 100% locally using a local deterministic Error Explainer Agent. No external AI API keys or third-party paid subscriptions are required.

---

## 🔄 Error Analysis Workflow (Error Explainer Agent)

The application relies on a single **Error Explainer Agent** to execute the end-to-end analysis:

1. **User Input**: Developer enters or pastes an error message, stack trace, code snippet, and optional language.
2. **Error Classification**: Error Explainer Agent categorizes the error type (`error_type`).
3. **What Happened**: Explains the issue in clear, simple developer terms (`what_happened`).
4. **Root Cause Analysis**: Determines why the error occurred (`why_it_happened`).
5. **How to Fix It**: Generates step-by-step resolution instructions (`how_to_fix_it`).
6. **Corrected Code**: Provides a working refactored example code fix (`corrected_code`).
7. **Prevention Tips**: Offers actionable tips to prevent future recurrence (`prevention_tips`).

---

## 🎨 Version 1 Visual Identity & Brand System

This application incorporates the official **Version 1** visual identity:

- **Logo Mark**: Triangular geometric logo mark featuring three overlapping faceted ribbon segments surrounding a central triangular negative space.
- **Logotype**: "VERSION 1" in bold, uppercase, geometric sans-serif typography.
- **Primary Brand Colors**:
  - **Teal / Cyan Accent**: `#00B8B9` — Used for logo symbol, primary action buttons, key highlights, active tabs, and focus states.
  - **Dark Navy / Slate**: `#052C39` — Used for logotype, headers, dark UI cards, navigation, and high-contrast typography.
- **Surface & Backgrounds**:
  - **Main Background**: `#FFFFFF` (Crisp Light Mode)
  - **Card / Surface Background**: `#F4F8F9` (Soft Light Gray-Teal)
  - **Border / Divider**: `#E2E8F0`

---

## 📁 Project Structure

```
AI-Error-Explainer/
├── .claude/                  # Claude Code configurations and agent instructions
│   ├── agents/
│   │   └── developer.md      # Developer agent instructions
│   ├── commands/
│   │   ├── reviewer.md       # Reviewer agent command instructions
│   │   └── tester.md         # Tester agent command instructions
│   ├── agent-spec.md         # System agent specification
│   └── guardrail.md          # Security, quality, and style guardrails
├── docs/                     # Technical specifications and API documentation
│   ├── requirements.md       # Full functional & non-functional requirements
│   └── api_schema.json       # OpenAPI / JSON Schema definition for API endpoints
├── backend/                  # Django REST API
│   ├── config/               # Django project configuration & settings
│   ├── api/                  # API endpoints, serializers, views, and services
│   ├── manage.py             # Django CLI runner
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variable template
├── frontend/                 # React + Vite TypeScript frontend UI
│   ├── src/                  # Components, styles, assets, and hooks
│   ├── public/               # Static assets & Version 1 brand logo
│   ├── index.html            # Main HTML document
│   ├── vite.config.js        # Vite bundler configuration
│   └── package.json          # Node.js dependencies
├── CLAUDE.md                 # Primary project context & developer guidelines
└── README.md                 # Project documentation overview
```

---

## 🚀 Setup & Installation

### Backend Setup (Django REST Framework)

1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (if needed):
   ```bash
   copy .env.example .env
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the API development server:
   ```bash
   python manage.py runserver
   ```
   The backend API will be running at `http://localhost:8000/api/`

---

### Frontend Setup (React + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend UI will be running at `http://localhost:3000`

---

## 📡 API Specification & Output Payload

The API schemas are formally defined in [`docs/api_schema.json`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/docs/api_schema.json).

### Error Analysis Endpoint (`POST /api/explain/`)

- **Request Payload**:
  ```json
  {
    "error_message": "TypeError: Cannot read property 'map' of undefined",
    "stack_trace": "TypeError: Cannot read property 'map' of undefined\n    at UserList (UserList.tsx:14:18)",
    "code_snippet": "const UserList = ({ users }) => {\n  return <div>{users.map(u => <p key={u.id}>{u.name}</p>)}</div>;\n};",
    "language": "typescript"
  }
  ```
- **Response Payload (200 OK)**:
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

## 🛠️ Development with Claude Code

This codebase is managed using **Claude Code**. Guidelines and guardrails for Claude Code agents are documented in:
- [`CLAUDE.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/CLAUDE.md)
- [`.claude/guardrail.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/.claude/guardrail.md)
- [`.claude/agent-spec.md`](file:///c:/Users/admin/Desktop/AI-Error-Explainer/.claude/agent-spec.md)
