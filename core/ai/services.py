from core.ai.client import get_openai_client, get_openai_model
from core.models import AISuggestion, Job, QuoteRequest, ServiceTemplate, Estimate


SYSTEM_INSTRUCTIONS = """
You are the AI backbone for JCV Power Solutions and JCV Command Center.

You help Jared run an electrical contractor business.

Rules:
- Do not directly change production data.
- Create clear suggestions for Jared to review.
- Do not claim final NEC/code compliance.
- Mention code/permit items must be verified by the electrician.
- Keep output practical for residential and light commercial electrical work.
- Be specific, organized, and action-oriented.
"""


def chat_completion(messages, temperature=0.2):
    client = get_openai_client()

    response = client.responses.create(
        model=get_openai_model(),
        input=messages,
        temperature=temperature,
    )

    return response.output_text


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
1. Scope of work
2. Assumptions
3. Exclusions
4. Add-ons to consider
5. Permit/code verification note
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
Labor rate: ${service_template.labor_rate}
Material cost estimate: ${service_template.estimated_material_cost}
Material markup: {service_template.material_markup}
Sell price: ${service_template.default_price}
Notes: {service_template.notes}

Return:
1. Suggested material list
2. Estimated quantities
3. Add-ons to consider
4. Pricing risks
5. Permit/code reminders for electrician verification
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
1. Is this too low, fair, or high?
2. Recommended sell price
3. Missing add-ons
4. Profitability risks
5. Notes for a small electrical contractor
"""

    return generate_ai_suggestion(
        title=f"Pricing review for {service_template.name}",
        category="pricing",
        prompt=prompt,
        related_service_template=service_template,
    )


def generate_website_improvement_suggestion():
    service_templates = ServiceTemplate.objects.filter(active=True)[:80]

    services_text = "\n".join([
        f"- {s.name} | {s.category} | ${s.default_price}"
        for s in service_templates
    ])

    prompt = f"""
Review JCV Power Solutions' website/service offering strategy.

Active services:
{services_text}

Suggest:
1. Website sections to improve
2. Missing service pages
3. Better homepage wording
4. SEO city/service page ideas
5. FAQ ideas
6. Calls-to-action
7. Trust-building content
8. Priority order for updates
"""

    return generate_ai_suggestion(
        title="Website improvement review",
        category="website",
        prompt=prompt,
    )


def generate_business_review_suggestion():
    recent_jobs = Job.objects.all()[:20]
    recent_leads = QuoteRequest.objects.all()[:20]
    recent_estimates = Estimate.objects.all()[:20]

    jobs_text = "\n".join([f"- {j.title} | {j.status} | ${j.estimated_total_price}" for j in recent_jobs])
    leads_text = "\n".join([f"- {l.name} | {l.service} | {l.status}" for l in recent_leads])
    estimates_text = "\n".join([f"- {e.title} | {e.status} | ${e.total}" for e in recent_estimates])

    prompt = f"""
Create a business improvement review for JCV Power Solutions.

Recent jobs:
{jobs_text}

Recent leads:
{leads_text}

Recent estimates:
{estimates_text}

Give:
1. What needs attention
2. Follow-up opportunities
3. Pricing/template improvements
4. Website/SEO opportunities
5. Operational improvements
6. Suggested next actions
"""

    return generate_ai_suggestion(
        title="AI business review",
        category="general",
        prompt=prompt,
    )