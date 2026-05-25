import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from core.models import AICommand, AICodeChange


ALLOWED_PREFIXES = [
    "core/",
    "mysite/",
    "templates/",
    "static/",
    "requirements.txt",
    "runtime.txt",
    "manage.py",
]

BLOCKED_PARTS = [
    ".env",
    "db.sqlite3",
    "project_structure.txt",
    "__pycache__",
    ".git/",
    "media/",
    ".venv/",
    "venv/",
    "env/",
    "staticfiles/",
    "secrets/",
    ".sqlite3",
    ".pyc",
]


def get_project_root():
    return Path(settings.BASE_DIR).resolve()


def normalize_path(file_path):
    return file_path.replace("\\", "/").strip()


def is_safe_path(file_path):
    normalized = normalize_path(file_path)

    if not normalized:
        return False

    if normalized.startswith("/") or ".." in normalized:
        return False

    if any(blocked in normalized for blocked in BLOCKED_PARTS):
        return False

    return any(
        normalized == prefix or normalized.startswith(prefix)
        for prefix in ALLOWED_PREFIXES
    )


def run_command(command, cwd):
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    output = [
        f"$ {' '.join(command)}",
        result.stdout,
        result.stderr,
    ]

    return result.returncode, "\n".join(output)


def call_openai_for_code(command):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    system_prompt = """
You are the AI developer for JCV Power Solutions and the JCV Command Center Django project.

Return ONLY valid JSON.
Do not use markdown.
Do not explain outside JSON.

Return this exact format:
{
  "summary": "Short summary of what changed",
  "files": [
    {
      "file_path": "core/templates/dashboard.html",
      "action": "create|replace|delete",
      "notes": "Why this file changes",
      "content": "Full file content here"
    }
  ]
}

PROJECT STRUCTURE:
- Root files include manage.py, requirements.txt, runtime.txt.
- Main Django project folder is mysite/.
- Main Django app is core/.
- Core app has separate view files:
  - core/views.py
  - core/customer_views.py
  - core/job_views.py
  - core/estimate_views.py
  - core/invoice_views.py
  - core/task_views.py
  - core/views_ai.py
- URL files:
  - mysite/urls.py
  - core/urls.py
- Templates are mainly in:
  - core/templates/
  - core/templates/admin/
- Static files are mainly in:
  - core/static/
  - static/
- AI code lives in:
  - core/ai/
  - core/services/

ALLOWED FILE AREAS:
You may generate files inside:
- core/
- mysite/
- templates/
- static/
- requirements.txt
- runtime.txt
- manage.py

DO NOT TOUCH:
- .env
- db.sqlite3
- database files
- project_structure.txt
- media/
- .git/
- .venv/
- venv/
- env/
- staticfiles/
- __pycache__/
- secrets/
- compiled .pyc files

RULES:
- Always provide full replacement file content for create or replace actions.
- Keep JCV Power Solutions branding unless explicitly asked otherwise.
- Preserve existing routes and model behavior unless the user specifically asks to change them.
- Do not create migrations unless absolutely required.
- Prefer safe, production-ready Django code.
- Avoid huge rewrites unless the prompt asks for a major rebuild.
- If improving UI, prefer templates and CSS first.
- If adding workflow features, update the correct core view file and core/urls.py if needed.
- Do not invent unsafe file paths like views/dashboard.py.
"""

    user_prompt = f"""
Build this requested code change for the JCV Command Center Django project:

{command.prompt}
"""

    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise ValueError(error.read().decode("utf-8"))

    content = data["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"OpenAI did not return valid JSON. Response was: {content}")


def generate_code_changes(command_id):
    command = AICommand.objects.get(id=command_id)

    try:
        result = call_openai_for_code(command)

        command.summary = result.get("summary", "")
        command.status = "generated"
        command.generated_at = timezone.now()
        command.log = "Code changes generated successfully."
        command.save()

        command.code_changes.all().delete()

        for file_data in result.get("files", []):
            file_path = normalize_path(file_data.get("file_path", ""))
            action = file_data.get("action", "replace")

            if action not in ["create", "replace", "delete"]:
                raise ValueError(f"Unsupported action: {action}")

            if not is_safe_path(file_path):
                raise ValueError(f"Unsafe file path blocked: {file_path}")

            AICodeChange.objects.create(
                command=command,
                file_path=file_path,
                action=action,
                proposed_content=file_data.get("content", ""),
                notes=file_data.get("notes", ""),
                status="pending",
            )

        return f"Generated {command.code_changes.count()} code change(s)."

    except Exception as error:
        command.status = "failed"
        command.log = str(error)
        command.save()
        raise error


def apply_code_change(change_id):
    change = AICodeChange.objects.get(id=change_id)

    if not is_safe_path(change.file_path):
        raise ValueError(f"Unsafe file path blocked: {change.file_path}")

    root = get_project_root()
    target_path = (root / change.file_path).resolve()

    if not str(target_path).startswith(str(root)):
        raise ValueError("Resolved path escaped project root.")

    try:
        if target_path.exists():
            change.original_content = target_path.read_text(encoding="utf-8")

        if change.action in ["create", "replace"]:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(change.proposed_content or "", encoding="utf-8")

        elif change.action == "delete":
            if target_path.exists():
                target_path.unlink()

        else:
            raise ValueError(f"Unsupported action: {change.action}")

        change.status = "applied"
        change.applied_at = timezone.now()
        change.error = None
        change.save()

        return f"Applied {change.file_path}"

    except Exception as error:
        change.status = "failed"
        change.error = str(error)
        change.save()
        raise error


def apply_command_code_changes(command_id):
    command = AICommand.objects.get(id=command_id)
    applied = 0

    for change in command.code_changes.exclude(status="applied"):
        apply_code_change(change.id)
        applied += 1

    command.status = "applied"
    command.applied_at = timezone.now()
    command.log = f"Applied {applied} code change(s)."
    command.save()

    return command.log


def git_commit_and_push(command_id):
    command = AICommand.objects.get(id=command_id)
    root = get_project_root()

    if os.environ.get("AI_DEVELOPER_ALLOW_GIT_PUSH") != "true":
        raise ValueError("AI_DEVELOPER_ALLOW_GIT_PUSH is not set to true.")

    remote_url = os.environ.get("GIT_REMOTE_URL")

    if not remote_url:
        raise ValueError("GIT_REMOTE_URL is not set.")

    git_author_name = os.environ.get("GIT_AUTHOR_NAME", "Jared Veatch")
    git_author_email = os.environ.get("GIT_AUTHOR_EMAIL", "jared.veatch1@gmail.com")

    commit_message = f"AI Developer Mode: {command.title}"

    output = []

    setup_commands = [
        ["git", "config", "user.name", git_author_name],
        ["git", "config", "user.email", git_author_email],
    ]

    for cmd in setup_commands:
        returncode, command_output = run_command(cmd, root)
        output.append(command_output)

        if returncode != 0:
            command.log = "\n".join(output)
            command.save()
            raise ValueError("\n".join(output))

    git_commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
    ]

    for cmd in git_commands:
        returncode, command_output = run_command(cmd, root)
        output.append(command_output)

        if returncode != 0:
            lower_output = command_output.lower()

            if "nothing to commit" in lower_output or "no changes added to commit" in lower_output:
                command.log = "\n".join(output)
                command.save()
                return "Nothing to commit."

            command.log = "\n".join(output)
            command.save()
            raise ValueError("\n".join(output))

    push_command = [
        "git",
        "push",
        remote_url,
        "HEAD:main",
    ]

    returncode, push_output = run_command(push_command, root)
    output.append(push_output)

    if returncode != 0:
        command.log = "\n".join(output)
        command.save()
        raise ValueError("\n".join(output))

    command.status = "pushed"
    command.pushed_at = timezone.now()
    command.log = "\n".join(output)
    command.save()

    return command.log