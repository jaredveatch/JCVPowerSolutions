import json

from core.ai.scenarios.residential_service import find_best_scenario
from core.ai.services import chat_completion


def build_job_package(prompt):
    scenario_package = find_best_scenario(prompt)

    if scenario_package.get("scenario") != "Custom Electrical Job":
        return scenario_package

    return ai_custom_job_package(prompt)


def ai_custom_job_package(prompt):
    system_prompt = """
You are JARVIS for JCV Power Solutions.

You are a residential electrical service estimator and field checklist assistant.

The user will describe an electrical job.

Return ONLY valid JSON.

Use this exact format:

{
  "scenario": "Short job scenario name",
  "confidence": "low | medium | high",
  "materials": [
    {
      "name": "Material name",
      "qty": 1,
      "unit": "each",
      "reason": "Why this is needed"
    }
  ],
  "steps": [
    "Step-by-step installation or troubleshooting step"
  ],
  "questions": [
    "Clarifying question Jared should ask"
  ],
  "labor_hours_min": 1,
  "labor_hours_max": 3,
  "customer_scope": "Plain English customer-facing scope",
  "internal_notes": "Notes for Jared/electrician"
}

Rules:
- Think like a practical residential service electrician.
- Include realistic materials and consumables.
- Do not claim final NEC compliance.
- Say code, permit, and equipment requirements must be verified by the electrician.
- If wire size, breaker size, or load is unknown, say verify nameplate/load before final sizing.
- Do not overcomplicate small jobs.
- Do not include markdown.
- Do not include explanations outside JSON.
"""

    raw_response = chat_completion(
        [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        data = {
            "scenario": "Custom Electrical Job",
            "confidence": "low",
            "materials": [
                {
                    "name": "Misc Electrical Materials",
                    "qty": 1,
                    "unit": "allowance",
                    "reason": "JARVIS could not parse a clean material list.",
                },
                {
                    "name": "Wire Connectors / Consumables",
                    "qty": 1,
                    "unit": "allowance",
                    "reason": "General small parts for electrical work.",
                },
            ],
            "steps": [
                "Review customer request.",
                "Inspect existing electrical conditions.",
                "Verify power source, circuit capacity, and access.",
                "Build final material list after site verification.",
                "Complete approved work.",
                "Test operation.",
                "Document findings.",
            ],
            "questions": [
                "What exactly needs to be installed, replaced, or diagnosed?",
                "Is there existing power at the location?",
                "Is attic, crawlspace, garage, or wall access available?",
            ],
            "labor_hours_min": 1,
            "labor_hours_max": 4,
            "customer_scope": prompt,
            "internal_notes": raw_response,
        }

    return normalize_package(data, prompt)


def normalize_package(data, prompt):
    return {
        "scenario": data.get("scenario") or "Custom Electrical Job",
        "confidence": data.get("confidence") or "medium",
        "materials": data.get("materials") or [],
        "steps": data.get("steps") or [],
        "questions": data.get("questions") or [],
        "labor_hours_min": data.get("labor_hours_min") or 1,
        "labor_hours_max": data.get("labor_hours_max") or 3,
        "customer_scope": data.get("customer_scope") or prompt,
        "internal_notes": data.get("internal_notes") or "Verify code, permit, access, and material requirements before final pricing.",
    }