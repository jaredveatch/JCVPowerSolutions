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
]

BLOCKED_PARTS = [
    ".env",
    "db.sqlite3",
    "__pycache__",
    ".git/",
    "media/",
]


def get_project_root():
    return Path(settings.BASE_DIR).resolve()


def is_safe_path(file_path):
    normalized = file_path.replace("\\", "/").strip()

    if normalized.startswith("/") or ".." in normalized:
        return False

    if any(part in normalized for part in BLOCKED_PARTS):
        return False

    return any(normalized.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def call_openai_for_code(command):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    system_prompt = """
You are an expert Django developer for JCV Power Solutions.
Return ONLY valid JSON.
Do not use markdown.

Return this format:
{
  "summary": "Short summary",
  "files": [
    {
      "file_path": "core/example.py",
      "action": "create",
      "notes": "Why this file changes",
      "content": "Full file content here"
    }
  ]
}

Rules:
- Only generate files inside core/, mysite/, templates/, or static/.
- Never touch .env, database files, media files, or .git.
- Always provide full replacement file content for create/replace.
- Keep changes safe for production Django.
"""

    user_prompt = f"""
Build this requested code change for the JCV Command Center Django project:

{command.prompt}
"""

    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
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
    return json.loads(content)


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
            file_path = file_data.get("file_path", "").strip()

            if not is_safe_path(file_path):
                raise ValueError(f"Unsafe file path blocked: {file_path}")

            AICodeChange.objects.create(
                command=command,
                file_path=file_path,
                action=file_data.get("action", "replace"),
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

    commit_message = f"AI Developer Mode: {command.title}"

    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push"],
    ]

    output = []

    for cmd in commands:
        result = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
        )

        output.append(f"$ {' '.join(cmd)}")
        output.append(result.stdout)
        output.append(result.stderr)

        if result.returncode != 0 and "nothing to commit" not in result.stdout.lower():
            raise ValueError("\n".join(output))

    command.status = "pushed"
    command.pushed_at = timezone.now()
    command.log = "\n".join(output)
    command.save()

    return command.log