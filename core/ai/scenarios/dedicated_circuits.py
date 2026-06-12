TRIGGERS = [
    "dedicated circuit",
    "microwave circuit",
    "freezer circuit",
    "garage outlet",
    "garage outlets",
    "mini split",
    "minisplit",
    "20 amp circuit",
    "240v circuit",
    "240 volt",
]


def matches(prompt):
    return any(trigger in prompt for trigger in TRIGGERS)


def build(prompt):
    prompt_lower = prompt.lower()

    breaker = "20A Single Pole Breaker"
    wire = "12/2 NM-B Cable"
    device = "20A Duplex Receptacle"
    voltage = "120V"

    if "mini" in prompt_lower or "240" in prompt_lower:
        breaker = "2-Pole Breaker - Verify Amperage"
        wire = "Cable Sized Per Equipment Nameplate"
        device = "Disconnect / Equipment Whip As Required"
        voltage = "240V"

    return {
        "scenario": "Dedicated Circuit",
        "confidence": "medium",
        "materials": [
            {"name": breaker, "qty": 1, "unit": "each", "reason": "Breaker for new dedicated circuit."},
            {"name": wire, "qty": 75, "unit": "ft", "reason": "Circuit wiring allowance. Verify final route distance."},
            {"name": device, "qty": 1, "unit": "each", "reason": "Endpoint device for equipment/location."},
            {"name": "Electrical Box", "qty": 1, "unit": "each", "reason": "Device box or equipment connection point."},
            {"name": "Cover Plate", "qty": 1, "unit": "each", "reason": "Finished cover."},
            {"name": "Wire Connectors / Staples / Consumables", "qty": 1, "unit": "allowance", "reason": "Small parts for installation."},
        ],
        "steps": [
            "Confirm equipment load, voltage, amperage, and location.",
            "Verify panel capacity and available breaker space.",
            "Plan route from panel to new outlet or equipment.",
            "Install breaker, cable, box, and receptacle/disconnect.",
            "Secure and protect cable where accessible.",
            "Terminate conductors.",
            "Label panel directory.",
            "Test voltage and operation.",
            "Review installation with customer.",
        ],
        "questions": [
            "What equipment is this circuit for?",
            "Is it 120V or 240V?",
            "What amperage does the equipment require?",
            "How far is the panel from the new location?",
            "Is there attic, crawlspace, or garage access?",
            "Is the panel full?",
        ],
        "labor_hours_min": 3,
        "labor_hours_max": 6,
        "customer_scope": f"Install new dedicated {voltage} circuit from electrical panel to requested equipment/location, including breaker, wiring, final device, testing, and labeling.",
        "internal_notes": "Verify equipment nameplate before final breaker/wire sizing. Check GFCI/AFCI requirements by location.",
    }