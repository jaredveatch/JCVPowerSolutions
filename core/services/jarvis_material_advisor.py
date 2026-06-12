from decimal import Decimal
from collections import defaultdict

from core.models import AISuggestion, MaterialCatalog


D = Decimal


def d(value):
    return D(str(value))


def normalize(text):
    return (text or "").lower().strip()


def contains_any(text, words):
    return any(word in text for word in words)


def material_line(name, qty, reason, priority="recommended"):
    return {
        "material_name": name,
        "quantity": str(d(qty)),
        "reason": reason,
        "priority": priority,
    }


JARVIS_RULES = [
    {
        "name": "Panel & Service Upgrade Intelligence",
        "triggers": ["panel", "service upgrade", "meter", "main breaker", "load center", "service entrance"],
        "required": [
            material_line("Square D Homeline 200A Indoor Main Breaker Panel 40/80", 1, "Core panel equipment.", "required"),
            material_line("Square D Homeline Ground Bar Kit", 1, "Panel grounding bar may be needed.", "required"),
            material_line("Square D Homeline Filler Plates", 4, "Unused breaker spaces must be filled.", "required"),
            material_line("8 ft Ground Rod", 2, "Grounding electrode system allowance.", "required"),
            material_line("Ground Rod Clamp", 2, "One clamp per ground rod.", "required"),
            material_line("#6 Bare Copper Ground Wire", 40, "Grounding electrode conductor allowance.", "required"),
            material_line("Water Pipe Ground Clamp", 1, "Bond metal water piping where applicable.", "recommended"),
            material_line("Intersystem Bonding Bridge", 1, "Required bonding point for low-voltage systems.", "recommended"),
        ],
        "recommended": [
            material_line("Square D Homeline Whole Home Surge Protector", 1, "Good upsell and modern panel upgrade add-on.", "recommended"),
            material_line("Square D Homeline 20A Single Pole Breaker", 6, "Common replacement breaker allowance.", "recommended"),
            material_line("Square D Homeline 15A Single Pole Breaker", 4, "Common lighting/general-purpose breaker allowance.", "recommended"),
            material_line("Square D Homeline 30A Two Pole Breaker", 1, "Common HVAC/dryer/appliance breaker allowance.", "optional"),
            material_line("Square D Homeline 50A Two Pole Breaker", 1, "Common range/EV/spare breaker allowance.", "optional"),
            material_line("2 Inch Weatherhead", 1, "Needed if overhead service mast/weatherhead is being touched.", "conditional"),
            material_line("2 Inch Rigid Service Mast", 1, "Needed if mast replacement is part of scope.", "conditional"),
            material_line("2 Inch Service Entrance Strap", 4, "Service mast/conduit support.", "conditional"),
            material_line("2 Inch Rigid Bushing", 2, "Rigid conduit terminations need bushings.", "conditional"),
            material_line("2 Inch Rigid Locknut", 2, "Rigid conduit terminations need locknuts.", "conditional"),
        ],
        "red_flags": [
            "Verify utility requirements before quoting final service equipment.",
            "Verify indoor vs outdoor panel before ordering.",
            "Verify breaker compatibility and existing circuit count.",
            "Verify working clearance before installation.",
            "Verify grounding/bonding requirements and permit/inspection requirements.",
        ],
    },
    {
        "name": "EV Charger Intelligence",
        "triggers": ["ev", "tesla", "charger", "wall connector", "14-50", "nema"],
        "required": [
            material_line("Tesla Wall Connector", 1, "Default EVSE allowance.", "required"),
            material_line("Square D Homeline 60A Two Pole Breaker", 1, "Common breaker for hardwired EV charger.", "required"),
            material_line("#6 THHN Copper Black", 120, "Hot conductor allowance.", "required"),
            material_line("#6 THHN Copper White", 60, "Second conductor / neutral allowance depending on charger type.", "required"),
            material_line("#10 THHN Copper Green", 60, "Equipment grounding conductor allowance.", "required"),
        ],
        "recommended": [
            material_line("3/4 PVC Conduit Schedule 40", 6, "Typical exterior conduit allowance.", "recommended"),
            material_line("3/4 PVC LB", 1, "Exterior wall penetration / direction change.", "recommended"),
            material_line("3/4 PVC Male Adapter", 2, "PVC termination fittings.", "recommended"),
            material_line("3/4 PVC Coupling", 2, "PVC joining fittings.", "recommended"),
            material_line("Duct Seal", 1, "Seal wall penetrations.", "recommended"),
            material_line("Masonry Anchors", 8, "Needed if mounting to brick/block/stucco.", "conditional"),
            material_line("Zip Ties", 10, "Cable/conduit organization.", "optional"),
        ],
        "red_flags": [
            "Verify load calculation before adding EV charger.",
            "Verify charger amperage settings.",
            "Verify indoor vs outdoor mounting.",
            "Verify GFCI requirements depending on receptacle vs hardwired installation.",
        ],
    },
    {
        "name": "Dedicated Circuit Intelligence",
        "triggers": ["dedicated circuit", "dedicated", "new circuit", "home run", "appliance circuit"],
        "required": [
            material_line("12/2 NM-B Cable", 75, "Default 20A dedicated circuit cable allowance.", "required"),
            material_line("Square D Homeline 20A Single Pole Breaker", 1, "Default 20A circuit breaker.", "required"),
            material_line("20A Tamper Resistant Receptacle", 1, "Default endpoint device.", "required"),
            material_line("1-Gang Plastic Nail-On Box", 1, "Device box.", "required"),
            material_line("1-Gang Decora Plate", 1, "Device plate.", "required"),
            material_line("Yellow Wire Nuts", 4, "Splicing allowance.", "recommended"),
            material_line("NM Cable Staples", 15, "Cable securing allowance.", "recommended"),
        ],
        "recommended": [
            material_line("GFCI Receptacle", 1, "May be required in garage, kitchen, exterior, laundry, or wet areas.", "conditional"),
            material_line("Square D Homeline 20A GFCI Breaker", 1, "Alternative GFCI protection at panel.", "conditional"),
            material_line("Square D Homeline 20A Dual Function Breaker", 1, "May be required where AFCI/GFCI protection is needed.", "conditional"),
        ],
        "red_flags": [
            "Verify AFCI/GFCI requirements by room and outlet location.",
            "Verify route length before final wire quantity.",
            "Verify panel capacity and available spaces.",
        ],
    },
    {
        "name": "Recessed Lighting Intelligence",
        "triggers": ["recessed", "wafer", "can light", "lighting"],
        "required": [
            material_line("6 Inch LED Recessed Wafer Light", 6, "Default six-light room kit.", "required"),
            material_line("14/2 NM-B Cable", 100, "Lighting circuit cable allowance.", "required"),
            material_line("Single Pole Switch", 1, "Switching control.", "required"),
            material_line("1-Gang Toggle Plate", 1, "Switch plate.", "required"),
            material_line("Blue Wire Nuts", 12, "Splicing allowance.", "recommended"),
            material_line("NM Cable Staples", 20, "Cable securing allowance.", "recommended"),
        ],
        "recommended": [
            material_line("Dimmer Switch", 1, "Recommended upgrade for recessed lighting.", "recommended"),
            material_line("6 Inch LED Trim Kit", 6, "Needed if using can housings instead of wafer lights.", "conditional"),
            material_line("6 Inch Recessed Can Housing", 6, "Needed if customer wants traditional cans.", "conditional"),
        ],
        "red_flags": [
            "Verify insulation/contact rating requirements.",
            "Verify ceiling access before quoting labor.",
            "Verify switch leg and power source location.",
        ],
    },
    {
        "name": "Exterior Electrical Intelligence",
        "triggers": ["exterior", "outdoor", "weatherproof", "outside", "patio", "garage exterior"],
        "required": [
            material_line("Exterior Bell Box", 1, "Weatherproof exterior box.", "required"),
            material_line("Weather Resistant GFCI Receptacle", 1, "Outdoor GFCI receptacle.", "required"),
            material_line("Weatherproof While-In-Use Extra Duty Cover", 1, "Required in-use weatherproof cover.", "required"),
        ],
        "recommended": [
            material_line("1/2 PVC Conduit Schedule 40", 2, "Exterior raceway allowance.", "recommended"),
            material_line("1/2 PVC Male Adapter", 2, "PVC box terminations.", "recommended"),
            material_line("Duct Seal", 1, "Seal exterior penetrations.", "recommended"),
            material_line("Masonry Anchors", 6, "Mounting hardware for masonry/stucco.", "conditional"),
            material_line("Yellow Wire Nuts", 4, "Splicing allowance.", "recommended"),
        ],
        "red_flags": [
            "Outdoor receptacles generally require weather-resistant devices and in-use covers.",
            "Seal penetrations to prevent water intrusion.",
            "Verify GFCI protection location.",
        ],
    },
    {
        "name": "Generator Intelligence",
        "triggers": ["generator", "backup power", "interlock", "inlet"],
        "required": [
            material_line("Generator Inlet 50A", 1, "Generator connection inlet.", "required"),
            material_line("Square D Homeline Generator Interlock Kit 150-225A Indoor", 1, "Interlock for backfeed setup.", "required"),
            material_line("Square D Homeline 50A Two Pole Breaker", 1, "Generator backfeed breaker.", "required"),
        ],
        "recommended": [
            material_line("Generator Power Cord 50A", 1, "Customer may need matching cord.", "recommended"),
            material_line("#6 THHN Copper Black", 80, "Generator feeder conductor allowance.", "recommended"),
            material_line("#6 THHN Copper White", 40, "Neutral conductor allowance.", "recommended"),
            material_line("#10 THHN Copper Green", 40, "Ground conductor allowance.", "recommended"),
            material_line("1 Inch PVC Conduit Schedule 40", 4, "Raceway allowance.", "recommended"),
            material_line("1 Inch PVC LB", 1, "Exterior wall penetration / direction change.", "recommended"),
        ],
        "red_flags": [
            "Never install generator backfeed without listed interlock/transfer method.",
            "Verify neutral configuration and bonding.",
            "Verify generator plug/inlet amperage.",
        ],
    },
    {
        "name": "Grounding & Bonding Intelligence",
        "triggers": ["ground", "bond", "bonding", "ground rod", "ufer"],
        "required": [
            material_line("8 ft Ground Rod", 2, "Grounding electrode allowance.", "required"),
            material_line("Ground Rod Clamp", 2, "One clamp per ground rod.", "required"),
            material_line("#6 Bare Copper Ground Wire", 50, "Grounding electrode conductor.", "required"),
            material_line("Water Pipe Ground Clamp", 1, "Bond metal water piping.", "recommended"),
            material_line("Intersystem Bonding Bridge", 1, "Bonding bridge for communication systems.", "recommended"),
        ],
        "recommended": [
            material_line("Bonding Bushing 1 Inch", 1, "May be required for service raceway bonding.", "conditional"),
            material_line("Anti-Ox Compound", 1, "Use for aluminum conductor terminations.", "conditional"),
        ],
        "red_flags": [
            "Verify service grounding electrode system.",
            "Verify water pipe bonding requirements.",
            "Verify separately derived system bonding if transformers are involved.",
        ],
    },
    {
        "name": "Smart Home Intelligence",
        "triggers": ["smart", "caseta", "lutron", "leviton", "ring", "nest", "ecobee", "doorbell", "thermostat"],
        "required": [],
        "recommended": [
            material_line("Leviton Smart Switch", 1, "Smart switch option.", "recommended"),
            material_line("Lutron Caseta Dimmer", 1, "Smart dimming option.", "recommended"),
            material_line("Lutron Caseta Pico Remote", 1, "Remote control accessory.", "optional"),
            material_line("Lutron Smart Bridge", 1, "Required for app integration in many Caseta installs.", "conditional"),
            material_line("Ring Doorbell", 1, "Smart doorbell option.", "optional"),
            material_line("Nest Thermostat", 1, "Smart thermostat option.", "optional"),
            material_line("Doorbell Transformer", 1, "May be needed for smart doorbell power.", "conditional"),
        ],
        "red_flags": [
            "Verify neutral availability in switch box.",
            "Verify Wi-Fi coverage and customer app setup expectations.",
            "Verify transformer voltage for smart doorbells.",
        ],
    },
    {
        "name": "Pool/Spa Intelligence",
        "triggers": ["pool", "spa", "hot tub", "jacuzzi"],
        "required": [
            material_line("60A Spa Panel", 1, "Spa disconnect/GFCI equipment.", "required"),
            material_line("Spa Disconnect GFCI", 1, "Required spa disconnect protection.", "required"),
            material_line("Equipotential Bonding Clamp", 4, "Pool/spa bonding allowance.", "required"),
            material_line("#8 THHN Copper Green", 100, "Bonding conductor allowance.", "required"),
        ],
        "recommended": [
            material_line("Pool Timer", 1, "Common pool equipment control.", "optional"),
            material_line("Pool Disconnect", 1, "Disconnecting means for pool equipment.", "conditional"),
            material_line("1 Inch PVC Conduit Schedule 40", 4, "Outdoor raceway allowance.", "recommended"),
            material_line("1 Inch PVC LB", 1, "Raceway body.", "recommended"),
        ],
        "red_flags": [
            "Pools and spas have strict bonding/GFCI requirements.",
            "Verify required disconnect location and working clearance.",
            "Verify equipment nameplate amperage.",
        ],
    },
]


QUANTITY_UPGRADE_RULES = [
    {
        "triggers": ["80 feet", "80 ft", "100 feet", "100 ft", "long run"],
        "materials": [
            ("#6 THHN Copper Black", 180, "Long EV/generator runs may need increased conductor footage."),
            ("#6 THHN Copper White", 90, "Long run neutral/second conductor allowance."),
            ("#10 THHN Copper Green", 90, "Long run ground conductor allowance."),
        ],
    },
    {
        "triggers": ["brick", "block", "masonry", "stucco"],
        "materials": [
            ("Masonry Anchors", 8, "Masonry mounting detected in notes."),
        ],
    },
    {
        "triggers": ["outdoor", "outside", "exterior"],
        "materials": [
            ("Duct Seal", 1, "Exterior penetration sealing recommended."),
            ("Weatherproof In-Use Cover", 1, "Outdoor receptacle/weatherproofing allowance."),
        ],
    },
]


def get_job_text(job):
    parts = [
        job.template.name if job.template else "",
        job.title,
        job.description,
        job.site_notes,
        job.material_notes,
        job.job_address,
    ]
    return normalize(" ".join([str(p or "") for p in parts]))


def get_existing_materials(job):
    existing = {}
    for item in job.job_materials.select_related("material").all():
        existing[item.material.name] = item
    return existing


def get_catalog():
    return {
        material.name: material
        for material in MaterialCatalog.objects.filter(active=True)
    }


def build_recommendations(job):
    text = get_job_text(job)
    existing = get_existing_materials(job)
    catalog = get_catalog()

    add_actions = []
    update_actions = []
    red_flags = []
    matched_rules = []

    seen_adds = set()

    for rule in JARVIS_RULES:
        if not contains_any(text, rule["triggers"]):
            continue

        matched_rules.append(rule["name"])
        red_flags.extend(rule.get("red_flags", []))

        for item in rule.get("required", []) + rule.get("recommended", []):
            material_name = item["material_name"]

            if material_name in seen_adds:
                continue

            if material_name not in catalog:
                continue

            if material_name in existing:
                continue

            seen_adds.add(material_name)

            material = catalog[material_name]

            add_actions.append({
                "action": "add_material",
                "material_id": material.id,
                "material_name": material.name,
                "quantity": item["quantity"],
                "reason": item["reason"],
                "priority": item["priority"],
                "unit_cost": str(material.unit_cost),
                "sell_price": str(material.sell_price),
            })

    for rule in QUANTITY_UPGRADE_RULES:
        if not contains_any(text, rule["triggers"]):
            continue

        for material_name, suggested_qty, reason in rule["materials"]:
            if material_name not in catalog:
                continue

            existing_item = existing.get(material_name)

            if existing_item:
                current_qty = d(existing_item.quantity or 0)
                if current_qty < d(suggested_qty):
                    update_actions.append({
                        "action": "update_quantity",
                        "job_material_id": existing_item.id,
                        "material_name": material_name,
                        "current_quantity": str(current_qty),
                        "suggested_quantity": str(d(suggested_qty)),
                        "reason": reason,
                        "priority": "recommended",
                    })
            else:
                material = catalog[material_name]
                add_actions.append({
                    "action": "add_material",
                    "material_id": material.id,
                    "material_name": material.name,
                    "quantity": str(d(suggested_qty)),
                    "reason": reason,
                    "priority": "recommended",
                    "unit_cost": str(material.unit_cost),
                    "sell_price": str(material.sell_price),
                })

    return {
        "matched_rules": matched_rules,
        "add_actions": add_actions,
        "update_actions": update_actions,
        "red_flags": sorted(set(red_flags)),
    }


def format_suggestion(job, result):
    lines = []
    lines.append("JARVIS Material Review")
    lines.append("")
    lines.append(f"Job: {job.title}")
    lines.append(f"Template: {job.template.name if job.template else 'None'}")
    lines.append("")

    if result["matched_rules"]:
        lines.append("Matched intelligence rules:")
        for rule in result["matched_rules"]:
            lines.append(f"- {rule}")
        lines.append("")

    if result["add_actions"]:
        lines.append("Recommended material additions:")
        for action in result["add_actions"]:
            lines.append(
                f"- ADD {action['material_name']} x {action['quantity']} "
                f"({action['priority']}) — {action['reason']}"
            )
        lines.append("")

    if result["update_actions"]:
        lines.append("Recommended quantity changes:")
        for action in result["update_actions"]:
            lines.append(
                f"- UPDATE {action['material_name']} from {action['current_quantity']} "
                f"to {action['suggested_quantity']} — {action['reason']}"
            )
        lines.append("")

    if result["red_flags"]:
        lines.append("JARVIS red flags / checks:")
        for flag in result["red_flags"]:
            lines.append(f"- {flag}")
        lines.append("")

    if not result["add_actions"] and not result["update_actions"]:
        lines.append(
            "No obvious missing materials were found based on the job template, "
            "current materials, and notes."
        )

    lines.append("JARVIS did not modify the job. Review and approve changes before applying.")

    return "\n".join(lines)


def create_jarvis_material_suggestion(job):
    result = build_recommendations(job)
    suggestion = format_suggestion(job, result)

    payload_actions = result["add_actions"] + result["update_actions"]

    return AISuggestion.objects.create(
        title=f"JARVIS Material Review - {job.title}",
        category="materials",
        prompt=(
            "Review the job template, current job materials, description, site notes, "
            "material notes, and address. Recommend missing materials or quantity changes. "
            "Do not directly modify the job."
        ),
        suggestion=suggestion,
        related_customer=job.customer,
        related_job=job,
        related_service_template=job.template,
        action_type="jarvis_material_review",
        action_payload={
            "job_id": job.id,
            "matched_rules": result["matched_rules"],
            "red_flags": result["red_flags"],
            "actions": payload_actions,
        },
    )