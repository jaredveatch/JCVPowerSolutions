from decimal import Decimal

from django.utils import timezone

from core.models import (
    AISuggestion,
    EstimateLineItem,
    JobMaterial,
    MaterialCatalog,
    ServiceTemplate,
    ServiceTemplateMaterial,
    Task,
)


def apply_ai_suggestion(suggestion_id):
    suggestion = AISuggestion.objects.get(id=suggestion_id)

    try:
        if not suggestion.action_type:
            raise ValueError("No action_type set on this AI suggestion.")

        payload = suggestion.action_payload or {}

        if suggestion.action_type == "create_task":
            result = apply_create_task(suggestion, payload)

        elif suggestion.action_type == "update_estimate_scope":
            result = apply_update_estimate_scope(suggestion, payload)

        elif suggestion.action_type == "update_pricing":
            result = apply_update_pricing(suggestion, payload)

        elif suggestion.action_type == "create_material":
            result = apply_create_material(suggestion, payload)

        elif suggestion.action_type == "create_template_material":
            result = apply_create_template_material(suggestion, payload)

        elif suggestion.action_type == "add_estimate_line_item":
            result = apply_add_estimate_line_item(suggestion, payload)

        elif suggestion.action_type == "add_job_material":
            result = apply_add_job_material(suggestion, payload)

        else:
            raise ValueError(f"Unsupported action_type: {suggestion.action_type}")

        suggestion.status = "applied"
        suggestion.reviewed_at = timezone.now()
        suggestion.reason = f"{suggestion.reason or ''}\n\nAPPLY RESULT: {result}".strip()
        suggestion.save()

        return result

    except Exception as error:
        suggestion.status = "rejected"
        suggestion.reviewed_at = timezone.now()
        suggestion.reason = f"{suggestion.reason or ''}\n\nAPPLY ERROR: {error}".strip()
        suggestion.save()
        raise error


def apply_create_task(suggestion, payload):
    task = Task.objects.create(
        title=payload.get("title") or suggestion.title,
        customer=suggestion.related_customer,
        job=suggestion.related_job,
        assigned_to=payload.get("assigned_to"),
        priority=payload.get("priority", "normal"),
        status=payload.get("status", "open"),
        due_date=payload.get("due_date"),
        notes=payload.get("notes") or suggestion.suggestion,
    )

    return f"Created task #{task.id}: {task.title}"


def apply_update_estimate_scope(suggestion, payload):
    estimate = suggestion.related_estimate

    if not estimate:
        raise ValueError("No related estimate attached to this AI suggestion.")

    estimate.scope_of_work = payload.get("scope_of_work") or suggestion.suggestion
    estimate.exclusions = payload.get("exclusions", estimate.exclusions)
    estimate.terms = payload.get("terms", estimate.terms)
    estimate.save()

    return f"Updated estimate scope for estimate #{estimate.id}"


def apply_update_pricing(suggestion, payload):
    template = suggestion.related_service_template

    if not template:
        raise ValueError("No related service template attached to this AI suggestion.")

    if "default_labor_hours" in payload:
        template.default_labor_hours = Decimal(str(payload["default_labor_hours"]))

    if "labor_rate" in payload:
        template.labor_rate = Decimal(str(payload["labor_rate"]))

    if "estimated_material_cost" in payload:
        template.estimated_material_cost = Decimal(str(payload["estimated_material_cost"]))

    if "material_markup" in payload:
        template.material_markup = Decimal(str(payload["material_markup"]))

    template.save()

    return f"Updated pricing for service template #{template.id}: {template.name}"


def apply_create_material(suggestion, payload):
    material = MaterialCatalog.objects.create(
        name=payload.get("name") or suggestion.title,
        manufacturer=payload.get("manufacturer"),
        part_number=payload.get("part_number"),
        description=payload.get("description") or suggestion.suggestion,
        unit=payload.get("unit", "each"),
        unit_cost=Decimal(str(payload.get("unit_cost", 0))),
        labor_hours=Decimal(str(payload.get("labor_hours", 0))),
        active=payload.get("active", True),
    )

    return f"Created material #{material.id}: {material.name}"


def apply_create_template_material(suggestion, payload):
    template = suggestion.related_service_template

    if not template:
        template_id = payload.get("service_template_id")
        if template_id:
            template = ServiceTemplate.objects.get(id=template_id)

    if not template:
        raise ValueError("No service template found for this suggestion.")

    material_id = payload.get("material_id")

    if not material_id:
        raise ValueError("Missing material_id in action_payload.")

    material = MaterialCatalog.objects.get(id=material_id)

    template_material, created = ServiceTemplateMaterial.objects.get_or_create(
        service_template=template,
        material=material,
        defaults={
            "quantity": Decimal(str(payload.get("quantity", 1))),
        },
    )

    if not created:
        template_material.quantity = Decimal(str(payload.get("quantity", template_material.quantity)))
        template_material.save()

    return f"Linked material {material.name} to template {template.name}"


def apply_add_estimate_line_item(suggestion, payload):
    estimate = suggestion.related_estimate

    if not estimate:
        raise ValueError("No related estimate attached to this AI suggestion.")

    line = EstimateLineItem.objects.create(
        estimate=estimate,
        item_type=payload.get("item_type", "service"),
        description=payload.get("description") or suggestion.title,
        quantity=Decimal(str(payload.get("quantity", 1))),
        unit_price=Decimal(str(payload.get("unit_price", 0))),
    )

    return f"Added estimate line item #{line.id}: {line.description}"


def apply_add_job_material(suggestion, payload):
    job = suggestion.related_job

    if not job:
        raise ValueError("No related job attached to this AI suggestion.")

    material_id = payload.get("material_id")

    if not material_id:
        raise ValueError("Missing material_id in action_payload.")

    material = MaterialCatalog.objects.get(id=material_id)

    job_material = JobMaterial.objects.create(
        job=job,
        material=material,
        quantity=Decimal(str(payload.get("quantity", 1))),
        unit_cost=Decimal(str(payload.get("unit_cost", material.unit_cost))),
        material_markup=Decimal(str(payload.get("material_markup", "1.35"))),
        labor_hours=Decimal(str(payload.get("labor_hours", material.labor_hours))),
        labor_rate=Decimal(str(payload.get("labor_rate", "110.00"))),
    )

    return f"Added job material #{job_material.id}: {material.name}"