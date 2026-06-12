TRIGGERS = [
    "ceiling fan",
    "fan install",
    "replace fan",
    "fan replacement",
    "install fan",
    "add fan",
]


def matches(prompt):
    return any(trigger in prompt for trigger in TRIGGERS)


def build(prompt):
    prompt_lower = prompt.lower()

    is_replacement = "replace" in prompt_lower or "replacement" in prompt_lower
    is_new_install = "new" in prompt_lower or "add fan" in prompt_lower or "no fan" in prompt_lower

    materials = [
        {
            "name": "Ceiling Fan Rated Box",
            "qty": 1,
            "unit": "each",
            "reason": "Fan requires a fan-rated support box.",
        },
        {
            "name": "Wire Connectors",
            "qty": 1,
            "unit": "pack",
            "reason": "For safe electrical terminations.",
        },
        {
            "name": "Misc Consumables",
            "qty": 1,
            "unit": "allowance",
            "reason": "Screws, connectors, tape, and small job materials.",
        },
    ]

    if is_new_install:
        materials.extend([
            {
                "name": "14/3 NM-B Cable",
                "qty": 50,
                "unit": "ft",
                "reason": "Typical cable for fan/light control on 15A lighting circuit.",
            },
            {
                "name": "Single Gang Switch Box",
                "qty": 1,
                "unit": "each",
                "reason": "Needed if adding a new wall switch.",
            },
            {
                "name": "Fan/Light Switch",
                "qty": 1,
                "unit": "each",
                "reason": "Control for fan and/or light.",
            },
            {
                "name": "Single Gang Cover Plate",
                "qty": 1,
                "unit": "each",
                "reason": "Finish plate for switch.",
            },
        ])

    return {
        "scenario": "Ceiling Fan",
        "confidence": "high",
        "materials": materials,
        "steps": [
            "Confirm fan location and customer expectations.",
            "Turn off power and verify circuit is de-energized.",
            "Remove existing fixture or fan if applicable.",
            "Verify box is fan-rated.",
            "Install fan-rated box or brace if needed.",
            "Make electrical connections.",
            "Mount ceiling fan securely.",
            "Install switch/control if included.",
            "Restore power and test fan, light, and controls.",
            "Clean work area.",
        ],
        "questions": [
            "Is this a replacement or brand-new fan location?",
            "Is the fan customer supplied?",
            "Is attic access available?",
            "Is there an existing switch?",
            "Does the customer want separate fan and light control?",
        ],
        "labor_hours_min": 1 if is_replacement else 3,
        "labor_hours_max": 2 if is_replacement else 5,
        "customer_scope": "Install or replace ceiling fan, verify fan-rated support, connect wiring, test operation, and clean work area.",
        "internal_notes": "Verify fan box rating. New installs may require attic access, wire fishing, switch leg, and drywall exclusions.",
    }