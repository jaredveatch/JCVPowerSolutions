from decimal import Decimal

from core.models import (
    JarvisJobReview,
    MaterialCatalog,
)


D = Decimal


def d(value):
    return D(str(value or 0))


def text_contains(text, words):
    text = (text or "").lower()
    return any(word in text for word in words)


def get_job_context_text(job, prompt=""):
    parts = [
        prompt,
        job.title,
        job.description,
        job.site_notes,
        job.material_notes,
        job.job_address,
        job.template.name if job.template else "",
    ]

    return " ".join([str(p or "") for p in parts]).lower()


def get_catalog_map():
    return {
        material.name: material
        for material in MaterialCatalog.objects.filter(active=True)
    }


def get_existing_material_map(job):
    return {
        item.material.name: item
        for item in job.job_materials.select_related("material").all()
    }


def add_action(material_name, quantity, reason, priority="recommended"):
    return {
        "action": "add_material",
        "material_name": material_name,
        "quantity": str(d(quantity)),
        "reason": reason,
        "priority": priority,
    }


def remove_action(job_material, reason, priority="recommended"):
    return {
        "action": "remove_material",
        "job_material_id": job_material.id,
        "material_name": job_material.material.name,
        "current_quantity": str(job_material.quantity),
        "reason": reason,
        "priority": priority,
    }


def update_action(job_material, suggested_quantity, reason, priority="recommended"):
    return {
        "action": "update_quantity",
        "job_material_id": job_material.id,
        "material_name": job_material.material.name,
        "current_quantity": str(job_material.quantity),
        "suggested_quantity": str(d(suggested_quantity)),
        "reason": reason,
        "priority": priority,
    }


def recommend_if_missing(actions, catalog, existing, material_name, quantity, reason, priority="recommended"):
    if material_name not in catalog:
        return

    if material_name in existing:
        return

    actions.append(add_action(material_name, quantity, reason, priority))


def recommend_quantity_if_low(actions, existing, material_name, suggested_quantity, reason, priority="recommended"):
    item = existing.get(material_name)

    if not item:
        return

    if d(item.quantity) < d(suggested_quantity):
        actions.append(update_action(item, suggested_quantity, reason, priority))


def panel_service_logic(text, actions, catalog, existing):
    if not text_contains(text, ["panel", "service upgrade", "service change", "meter", "load center"]):
        return []

    notes = [
        "Verify utility requirements before final material order.",
        "Verify panel location, working clearance, grounding, bonding, and permit requirements.",
        "Verify indoor vs outdoor panel before purchasing equipment.",
    ]

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 200A Main Breaker",
        1,
        "200A panel/service work may require a matching main breaker depending on selected panel.",
        "conditional",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 20A Single Pole Breaker",
        6,
        "Common branch breaker allowance for panel replacement.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 15A Single Pole Breaker",
        4,
        "Common lighting/general-purpose branch breaker allowance.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 30A Two Pole Breaker",
        1,
        "Common two-pole appliance/HVAC breaker allowance.",
        "optional",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 50A Two Pole Breaker",
        1,
        "Common two-pole range/generator/EV breaker allowance.",
        "optional",
    )

    if text_contains(text, ["overhead", "mast", "weatherhead", "service drop"]):
        recommend_if_missing(
            actions, catalog, existing,
            "2 Inch Weatherhead",
            1,
            "Overhead service detected.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "2 Inch Rigid Service Mast",
            1,
            "Overhead service may require mast replacement or mast material allowance.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "2 Inch Service Entrance Strap",
            4,
            "Service mast requires proper support straps.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "2 Inch Rigid Bushing",
            2,
            "Rigid service raceway terminations require bushings.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "2 Inch Rigid Locknut",
            2,
            "Rigid service raceway terminations require locknuts.",
            "recommended",
        )

    if text_contains(text, ["underground", "lateral", "meter only", "reuse mast"]):
        for material_name in [
            "2 Inch Weatherhead",
            "2 Inch Rigid Service Mast",
            "2 Inch Service Entrance Strap",
        ]:
            item = existing.get(material_name)
            if item:
                actions.append(
                    remove_action(
                        item,
                        "Underground/reuse condition detected; this overhead service material may not be needed.",
                        "conditional",
                    )
                )

    return notes


def generator_logic(text, actions, catalog, existing):
    if not text_contains(text, ["generator", "interlock", "backup power", "inlet"]):
        return []

    notes = [
        "Verify interlock compatibility with the exact panel cover.",
        "Verify generator inlet amperage and customer generator plug configuration.",
        "Verify neutral/ground bonding requirements for generator setup.",
    ]

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline Generator Interlock Kit 150-225A Indoor",
        1,
        "Generator interlock requested/detected.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Generator Inlet 50A",
        1,
        "Generator connection inlet likely needed.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Generator Power Cord 50A",
        1,
        "Customer may need matching generator cord.",
        "optional",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "Square D Homeline 50A Two Pole Breaker",
        1,
        "Generator inlet/interlock setup commonly uses a 2-pole breaker.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "#6 THHN Copper Black",
        80,
        "Generator feeder conductor allowance.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "#6 THHN Copper White",
        40,
        "Generator neutral conductor allowance.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "#10 THHN Copper Green",
        40,
        "Generator equipment grounding conductor allowance.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "1 Inch PVC Conduit Schedule 40",
        4,
        "Generator inlet raceway allowance.",
        "recommended",
    )

    recommend_if_missing(
        actions, catalog, existing,
        "1 Inch PVC LB",
        1,
        "Generator inlet wall penetration/direction change allowance.",
        "recommended",
    )

    return notes


def ev_logic(text, actions, catalog, existing):
    if not text_contains(text, ["ev", "tesla", "charger", "wall connector", "14-50"]):
        return []

    notes = [
        "Run a load calculation before committing to EV charger amperage.",
        "Verify hardwired charger vs NEMA 14-50 receptacle scope.",
        "Verify indoor/outdoor location and mounting surface.",
    ]

    if text_contains(text, ["14-50", "receptacle", "plug"]):
        recommend_if_missing(
            actions, catalog, existing,
            "NEMA 14-50 EV Receptacle",
            1,
            "NEMA 14-50 EV receptacle detected.",
            "required",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "Square D Homeline 50A Two Pole Breaker",
            1,
            "50A EV receptacle usually requires 2-pole breaker.",
            "required",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "6/3 NM-B Cable",
            60,
            "Typical 50A EV receptacle cable allowance.",
            "recommended",
        )
    else:
        recommend_if_missing(
            actions, catalog, existing,
            "Tesla Wall Connector",
            1,
            "Default hardwired EV charger allowance.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "Square D Homeline 60A Two Pole Breaker",
            1,
            "Common breaker for hardwired EV charger.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "#6 THHN Copper Black",
            120,
            "EV charger conductor allowance.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "#6 THHN Copper White",
            60,
            "Second conductor/neutral allowance depending on charger.",
            "recommended",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "#10 THHN Copper Green",
            60,
            "EV equipment grounding conductor allowance.",
            "recommended",
        )

    if text_contains(text, ["outdoor", "outside", "exterior"]):
        recommend_if_missing(
            actions, catalog, existing,
            "Duct Seal",
            1,
            "Exterior penetration sealing.",
            "recommended",
        )

    if text_contains(text, ["brick", "block", "masonry", "stucco"]):
        recommend_if_missing(
            actions, catalog, existing,
            "Masonry Anchors",
            8,
            "Masonry mounting surface detected.",
            "recommended",
        )

    return notes


def exterior_logic(text, actions, catalog, existing):
    if not text_contains(text, ["outdoor", "outside", "exterior", "weatherproof", "brick", "stucco"]):
        return []

    notes = [
        "Weatherproof all exterior devices and seal wall penetrations.",
        "Verify GFCI requirements for exterior outlets.",
    ]

    recommend_if_missing(
        actions, catalog, existing,
        "Duct Seal",
        1,
        "Exterior work detected; seal penetrations.",
        "recommended",
    )

    if text_contains(text, ["receptacle", "outlet", "plug"]):
        recommend_if_missing(
            actions, catalog, existing,
            "Weather Resistant GFCI Receptacle",
            1,
            "Outdoor receptacle should be weather-resistant/GFCI protected.",
            "required",
        )
        recommend_if_missing(
            actions, catalog, existing,
            "Weatherproof While-In-Use Extra Duty Cover",
            1,
            "Outdoor receptacle requires in-use cover.",
            "required",
        )

    if text_contains(text, ["brick", "block", "masonry", "stucco"]):
        recommend_if_missing(
            actions, catalog, existing,
            "Masonry Anchors",
            8,
            "Masonry/stucco mounting detected.",
            "recommended",
        )

    return notes


def cleanup_logic(text, actions, existing):
    notes = []

    if text_contains(text, ["reuse meter", "existing meter", "do not replace meter"]):
        item = existing.get("200A Meter Socket Ringless")
        if item:
            actions.append(
                remove_action(
                    item,
                    "Prompt suggests existing meter socket may be reused.",
                    "conditional",
                )
            )

    if text_contains(text, ["no surge", "remove surge", "customer declined surge"]):
        item = existing.get("Square D Homeline Whole Home Surge Protector")
        if item:
            actions.append(
                remove_action(
                    item,
                    "Customer declined surge protection or prompt says remove surge.",
                    "optional",
                )
            )

    return notes


def build_dashboard_recommendations(job, prompt):
    text = get_job_context_text(job, prompt)
    catalog = get_catalog_map()
    existing = get_existing_material_map(job)

    actions = []
    notes = []

    notes += panel_service_logic(text, actions, catalog, existing)
    notes += generator_logic(text, actions, catalog, existing)
    notes += ev_logic(text, actions, catalog, existing)
    notes += exterior_logic(text, actions, catalog, existing)
    notes += cleanup_logic(text, actions, existing)

    seen = set()
    unique_actions = []

    for action in actions:
        key = (
            action.get("action"),
            action.get("material_name"),
            action.get("job_material_id"),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_actions.append(action)

    summary = "JARVIS found recommendations." if unique_actions else "JARVIS found no obvious material changes."

    return {
        "summary": summary,
        "actions": unique_actions,
        "notes": sorted(set(notes)),
    }


def create_dashboard_jarvis_review(job, prompt):
    recommendations = build_dashboard_recommendations(job, prompt)

    return JarvisJobReview.objects.create(
        job=job,
        prompt=prompt,
        summary=recommendations["summary"],
        recommendations=recommendations,
        status="reviewed",
    )