from core.ai.client import get_openai_client, get_openai_model
from core.models import AISuggestion


SYSTEM_INSTRUCTIONS = """
You are the AI assistant for JCV Power Solutions and JCV Command Center.

You help with:
- electrical estimating
- material list suggestions
- labor hour suggestions
- scope of work writing
- exclusions
- service template ideas
- pricing review
- customer-facing wording
- website and SEO content

Rules:
- Do not make changes directly.
- Only generate suggestions for Jared to approve.
- Do not claim final NEC/code compliance.
- Any NEC/code-related output must say it needs electrician verification.
- Keep answers practical for residential and light commercial electrical work.
- Be clear, specific, and useful.
"""


def generate_ai_suggestion(
    *,
    title,
    category,
    prompt,
    related_customer=None,
    related_job=None,
    related_estimate=None,
    related_service_template=None,
):
    client = get_openai_client()

    response = client.responses.create(
        model=get_openai_model(),
        instructions=SYSTEM_INSTRUCTIONS,
        input=prompt,
    )

    return AISuggestion.objects.create(
        title=title,
        category=category,
        prompt=prompt,
        suggestion=response.output_text,
        related_customer=related_customer,
        related_job=related_job,
        related_estimate=related_estimate,
        related_service_template=related_service_template,
    )


def generate_job_scope_suggestion(job):
    prompt = f"""
Create a professional customer-facing electrical scope of work.

Job title: {job.title}
Customer: {job.customer}
Job description: {job.description}
Site notes: {job.site_notes}
Material notes: {job.material_notes}
Estimated price: ${job.estimated_total_price}

Include:
- scope of work
- assumptions
- exclusions
- permit/code verification note
"""

    return generate_ai_suggestion(
        title=f"Scope suggestion for {job.title}",
        category="scope",
        prompt=prompt,
        related_customer=job.customer,
        related_job=job,
    )


def generate_service_template_material_suggestion(service_template):
    prompt = f"""
Suggest a practical material package for this electrical service template.

Service: {service_template.name}
Category: {service_template.category}
Labor hours: {service_template.default_labor_hours}
Material cost estimate: ${service_template.estimated_material_cost}
Sell price: ${service_template.default_price}
Notes: {service_template.notes}

Return:
- suggested materials
- estimated quantities
- add-ons to consider
- pricing notes
- code/permit reminders for electrician verification
"""

    return generate_ai_suggestion(
        title=f"Material suggestion for {service_template.name}",
        category="materials",
        prompt=prompt,
        related_service_template=service_template,
    )


def generate_pricing_review_suggestion(service_template):
    prompt = f"""
Review this electrical service template pricing.

Service: {service_template.name}
Category: {service_template.category}
Labor hours: {service_template.default_labor_hours}
Labor rate: ${service_template.labor_rate}
Material cost: ${service_template.estimated_material_cost}
Material markup: {service_template.material_markup}
Calculated price: ${service_template.calculated_price}
Default sell price: ${service_template.default_price}
Permit required: {service_template.permit_required}

Give:
- whether pricing looks too low, fair, or high
- recommended pricing adjustment if needed
- risk items
- add-ons that should be separate
"""

    return generate_ai_suggestion(
        title=f"Pricing review for {service_template.name}",
        category="pricing",
        prompt=prompt,
        related_service_template=service_template,
    )