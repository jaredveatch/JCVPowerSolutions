TRIGGERS = [
    "recessed",
    "can light",
    "can lights",
    "wafer light",
    "wafer lights",
    "downlight",
    "downlights",
    "led lights",
]


def matches(prompt):
    return any(trigger in prompt for trigger in TRIGGERS)


def extract_quantity(prompt):
    for word in prompt.replace(",", " ").split():
        if word.isdigit():
            return int(word)
    return 4


def build(prompt):
    prompt_lower = prompt.lower()
    qty = extract_quantity(prompt)

    materials = [
        {
            "name": "LED Wafer Recessed Light",
            "qty": qty,
            "unit": "each",
            "reason": "Main recessed lighting fixtures.",
        },
        {
            "name": "14/2 NM-B Cable",
            "qty": max(50, qty * 15),
            "unit": "ft",
            "reason": "Typical lighting branch circuit wiring.",
        },
        {
            "name": "Wire Connectors",
            "qty": 1,
            "unit": "pack",
            "reason": "For splices and terminations.",
        },
        {
            "name": "NM Staples",
            "qty": 1,
            "unit": "box",
            "reason": "For securing cable where accessible.",
        },
        {
            "name": "Misc Consumables",
            "qty": 1,
            "unit": "allowance",
            "reason": "Small job materials.",
        },
    ]

    if "dimmer" in prompt_lower:
        materials.append({
            "name": "LED Compatible Dimmer Switch",
            "qty": 1,
            "unit": "each",
            "reason": "Customer requested dimming control.",
        })

    return {
        "scenario": "Recessed Lighting",
        "confidence": "high",
        "materials": materials,
        "steps": [
            "Confirm light count, locations, and switch location.",
            "Verify circuit capacity and existing switch wiring.",
            "Lay out light spacing.",
            "Check ceiling for joists, ducts, plumbing, and obstructions.",
            "Cut ceiling openings.",
            "Route cable between light locations.",
            "Install wafer junction boxes and make splices.",
            "Install lights.",
            "Install switch or dimmer if included.",
            "Restore power and test all lights.",
            "Clean work area.",
        ],
        "questions": [
            "How many lights does the customer want?",
            "Is attic access available?",
            "Is there an existing switch?",
            "Does the customer want a dimmer?",
            "Are lights customer supplied?",
            "Is drywall repair excluded?",
        ],
        "labor_hours_min": max(2, qty // 2),
        "labor_hours_max": max(4, qty // 2 + 3),
        "customer_scope": f"Install approximately {qty} recessed LED lights, route wiring, install controls as needed, test operation, and clean work area.",
        "internal_notes": "Confirm attic access and obstructions. Drywall repair should be excluded unless included.",
    }