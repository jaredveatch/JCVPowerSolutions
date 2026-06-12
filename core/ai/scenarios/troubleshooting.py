TRIGGERS = [
    "dead outlet",
    "dead outlets",
    "tripping breaker",
    "breaker trips",
    "flickering lights",
    "partial power",
    "lost power",
    "no power",
    "gfci trips",
    "outlets not working",
]


def matches(prompt):
    return any(trigger in prompt for trigger in TRIGGERS)


def build(prompt):
    prompt_lower = prompt.lower()

    materials = [
        {
            "name": "Standard Duplex Receptacle",
            "qty": 2,
            "unit": "each",
            "reason": "Common replacement during outlet troubleshooting.",
        },
        {
            "name": "GFCI Receptacle",
            "qty": 1,
            "unit": "each",
            "reason": "Common issue for dead kitchen, bathroom, garage, and exterior outlets.",
        },
        {
            "name": "Wire Connectors",
            "qty": 1,
            "unit": "pack",
            "reason": "For repairing loose or failed splices.",
        },
        {
            "name": "Cover Plates",
            "qty": 2,
            "unit": "each",
            "reason": "Replace damaged plates if needed.",
        },
        {
            "name": "Troubleshooting Consumables",
            "qty": 1,
            "unit": "allowance",
            "reason": "Small repair materials.",
        },
    ]

    if "breaker" in prompt_lower or "tripping" in prompt_lower:
        materials.append({
            "name": "Matching Breaker - Verify Panel Type",
            "qty": 1,
            "unit": "each",
            "reason": "Possible replacement only after diagnosis.",
        })

    return {
        "scenario": "Electrical Troubleshooting",
        "confidence": "medium",
        "materials": materials,
        "steps": [
            "Ask customer when the issue started and what changed.",
            "Identify all affected devices, rooms, and circuits.",
            "Check panel for tripped breakers or loose labeling.",
            "Check upstream GFCI devices.",
            "Test voltage at affected outlets, switches, or fixtures.",
            "Inspect for loose backstab connections, burnt devices, failed splices, or damaged wiring.",
            "Isolate load if breaker is tripping.",
            "Repair identified issue after customer approval.",
            "Test circuit under normal load.",
            "Document findings and recommendations.",
        ],
        "questions": [
            "When did the problem start?",
            "Did anything trip, spark, or smell burnt?",
            "Is it one outlet, one room, or multiple rooms?",
            "Any recent storms, remodeling, or appliance changes?",
            "Are any GFCIs tripped?",
            "Does the breaker trip instantly or only when a load is used?",
        ],
        "labor_hours_min": 1,
        "labor_hours_max": 3,
        "customer_scope": "Diagnose electrical issue, inspect affected circuit/devices, identify cause, and provide repair options. Minor repairs may be completed with approval.",
        "internal_notes": "Bill as diagnostic first. Do not promise repair until cause is found.",
    }