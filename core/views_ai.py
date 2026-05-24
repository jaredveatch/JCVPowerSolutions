from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .models import AISuggestion, Job, ServiceTemplate
from .ai.services import (
    generate_job_scope_suggestion,
    generate_service_template_material_suggestion,
    generate_pricing_review_suggestion,
    generate_website_improvement_suggestion,
    generate_business_review_suggestion,
)


@login_required
def ai_dashboard(request):
    suggestions = AISuggestion.objects.all()[:25]
    pending_count = AISuggestion.objects.filter(status="pending").count()
    approved_count = AISuggestion.objects.filter(status="approved").count()
    applied_count = AISuggestion.objects.filter(status="applied").count()

    jobs = Job.objects.all().order_by("-created_at")[:20]
    service_templates = ServiceTemplate.objects.filter(active=True).order_by("category", "name")[:30]

    return render(request, "ai_dashboard.html", {
        "suggestions": suggestions,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "applied_count": applied_count,
        "jobs": jobs,
        "service_templates": service_templates,
    })


@login_required
def ai_generate_job_scope(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    try:
        generate_job_scope_suggestion(job)
        messages.success(request, "AI scope suggestion created.")
    except Exception as exc:
        messages.error(request, f"AI error: {exc}")

    return redirect("ai_dashboard")


@login_required
def ai_generate_template_materials(request, template_id):
    service_template = get_object_or_404(ServiceTemplate, id=template_id)

    try:
        generate_service_template_material_suggestion(service_template)
        messages.success(request, "AI material suggestion created.")
    except Exception as exc:
        messages.error(request, f"AI error: {exc}")

    return redirect("ai_dashboard")


@login_required
def ai_review_template_pricing(request, template_id):
    service_template = get_object_or_404(ServiceTemplate, id=template_id)

    try:
        generate_pricing_review_suggestion(service_template)
        messages.success(request, "AI pricing review created.")
    except Exception as exc:
        messages.error(request, f"AI error: {exc}")

    return redirect("ai_dashboard")


@login_required
def ai_generate_website_review(request):
    try:
        generate_website_improvement_suggestion()
        messages.success(request, "AI website improvement review created.")
    except Exception as exc:
        messages.error(request, f"AI error: {exc}")

    return redirect("ai_dashboard")


@login_required
def ai_generate_business_review(request):
    try:
        generate_business_review_suggestion()
        messages.success(request, "AI business review created.")
    except Exception as exc:
        messages.error(request, f"AI error: {exc}")

    return redirect("ai_dashboard")