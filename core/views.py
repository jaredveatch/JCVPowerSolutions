from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.ai.jarvis_builder import build_job_package

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    Job,
    Estimate,
    EstimateLineItem,
    Invoice,
    Task,
    JobMaterial,
    JobNote,
    MaterialCatalog,
    JarvisJobReview,
)


def home(request):
    if request.method == "POST":
        if "quote_form" in request.POST:
            QuoteRequest.objects.create(
                name=request.POST.get("name"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                service=request.POST.get("service"),
                message=request.POST.get("message"),
                source="website",
            )

            return JsonResponse({
                "success": True,
                "message": "Thank you for submitting your request.",
            })

        if "career_form" in request.POST:
            CareerApplication.objects.create(
                name=request.POST.get("applicant_name"),
                phone=request.POST.get("applicant_phone"),
                email=request.POST.get("applicant_email"),
                position=request.POST.get("position"),
                experience=request.POST.get("experience"),
                license_info=request.POST.get("license"),
                message=request.POST.get("career_message"),
            )

            return JsonResponse({
                "success": True,
                "message": "Application submitted successfully.",
            })

    return render(request, "home.html")


@staff_member_required
def dashboard(request):
    today = timezone.now().date()

    new_quotes = QuoteRequest.objects.filter(status="new").order_by("-created_at")
    recent_leads = QuoteRequest.objects.order_by("-created_at")[:5]

    active_jobs = Job.objects.exclude(
        status__in=["completed", "cancelled", "paid"]
    )

    jobs_needing_quotes = Job.objects.filter(
        status__in=["site_visit", "estimate_needed"]
    ).order_by("-created_at")[:5]

    approved_jobs = Job.objects.filter(
        status="approved"
    ).order_by("-created_at")[:5]

    open_tasks = Task.objects.exclude(
        status__in=["done", "completed", "cancelled"]
    )

    open_invoices = Invoice.objects.exclude(status="paid")
    overdue_invoices = Invoice.objects.filter(
        due_date__lt=today
    ).exclude(status="paid")

    pending_estimates = Estimate.objects.filter(
        status__in=["draft", "sent"]
    )

    revenue_total = Invoice.objects.filter(
        status="paid"
    ).aggregate(total=Sum("total"))["total"] or 0

    outstanding_total = open_invoices.aggregate(
        total=Sum("amount_due")
    )["total"] or 0

    context = {
        "new_quotes": recent_leads,
        "recent_leads": recent_leads,
        "recent_jobs": Job.objects.order_by("-created_at")[:5],
        "recent_tasks": open_tasks.order_by("due_date", "-created_at")[:5],
        "jobs_needing_quotes": jobs_needing_quotes,
        "approved_jobs": approved_jobs,
        "overdue_invoices": overdue_invoices.order_by("due_date")[:5],

        "quotes_count": new_quotes.count(),
        "customers_count": Customer.objects.count(),
        "jobs_count": active_jobs.count(),
        "estimates_count": pending_estimates.count(),
        "invoices_count": open_invoices.count(),
        "open_tasks_count": open_tasks.count(),

        "total_jobs_count": Job.objects.count(),
        "total_estimates_count": Estimate.objects.count(),
        "total_invoices_count": Invoice.objects.count(),
        "jobs_needing_quotes_count": jobs_needing_quotes.count(),
        "approved_jobs_count": approved_jobs.count(),
        "overdue_invoices_count": overdue_invoices.count(),

        "revenue_total": revenue_total,
        "outstanding_total": outstanding_total,
    }

    return render(request, "dashboard.html", context)


@staff_member_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    customers = Customer.objects.none()
    jobs = Job.objects.none()
    invoices = Invoice.objects.none()
    estimates = Estimate.objects.none()
    quotes = QuoteRequest.objects.none()

    if query:
        customers = Customer.objects.filter(
            Q(name__icontains=query)
            | Q(company_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(address__icontains=query)
            | Q(city__icontains=query)
        )

        jobs = Job.objects.filter(
            Q(title__icontains=query)
            | Q(customer__name__icontains=query)
            | Q(customer__phone__icontains=query)
            | Q(job_address__icontains=query)
            | Q(description__icontains=query)
            | Q(site_notes__icontains=query)
        )

        invoices = Invoice.objects.filter(
            Q(invoice_number__icontains=query)
            | Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(job__title__icontains=query)
            | Q(job__customer__name__icontains=query)
        )

        estimates = Estimate.objects.filter(
            Q(title__icontains=query)
            | Q(scope_of_work__icontains=query)
            | Q(job__title__icontains=query)
            | Q(job__customer__name__icontains=query)
        )

        quotes = QuoteRequest.objects.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(service__icontains=query)
            | Q(message__icontains=query)
        )

    return render(request, "search_results.html", {
        "query": query,
        "customers": customers,
        "jobs": jobs,
        "invoices": invoices,
        "estimates": estimates,
        "quotes": quotes,
    })


# =========================================================
# JARVIS JOB BUILDER PIPELINE
# =========================================================

@staff_member_required
def jarvis_build_job_package(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method != "POST":
        return redirect("job_detail", job_id=job.id)

    prompt = request.POST.get("jarvis_prompt", "").strip()

    if not prompt:
        messages.error(request, "Tell JARVIS what the job is first.")
        return redirect("job_detail", job_id=job.id)

    package = build_job_package(prompt)

    review = JarvisJobReview.objects.create(
        job=job,
        prompt=prompt,
        summary=package.get("scenario", "JARVIS Job Package"),
        recommendations=package,
        status="reviewed",
    )

    JobNote.objects.create(
        job=job,
        author="JARVIS",
        note=f"""JARVIS built a job package.

Scenario:
{package.get("scenario")}

Labor:
{package.get("labor_hours_min")}–{package.get("labor_hours_max")} hours

Customer Scope:
{package.get("customer_scope")}

Internal Notes:
{package.get("internal_notes")}
""",
        internal=True,
    )

    messages.success(request, "JARVIS built the job package.")
    return redirect("job_detail", job_id=job.id)


@staff_member_required
def jarvis_apply_materials(request, review_id):
    review = get_object_or_404(JarvisJobReview, id=review_id)
    job = review.job
    package = review.recommendations or {}

    materials = package.get("materials", [])
    added = []

    for item in materials:
        name = item.get("name", "").strip()
        qty = Decimal(str(item.get("qty") or 1))
        unit = item.get("unit", "each")

        if not name:
            continue

        catalog_item = MaterialCatalog.objects.filter(
            name__icontains=name,
            active=True,
        ).first()

        if not catalog_item:
            catalog_item = MaterialCatalog.objects.create(
                name=name,
                category="JARVIS Generated",
                unit=unit,
                unit_cost=Decimal("0.00"),
                labor_hours=Decimal("0.00"),
                active=True,
            )

        JobMaterial.objects.create(
            job=job,
            material=catalog_item,
            quantity=qty,
            unit_cost=catalog_item.unit_cost,
            material_markup=catalog_item.material_markup,
            labor_hours=catalog_item.labor_hours,
        )

        added.append(f"- {qty} {unit} {name}")

    review.status = "applied"
    review.applied_at = timezone.now()
    review.save()

    JobNote.objects.create(
        job=job,
        author="JARVIS",
        note="JARVIS applied materials to this job:\n\n" + (
            "\n".join(added) if added else "No materials added."
        ),
        internal=True,
    )

    messages.success(request, "JARVIS materials applied to the job.")
    return redirect("job_detail", job_id=job.id)


@staff_member_required
def jarvis_create_estimate(request, review_id):
    review = get_object_or_404(JarvisJobReview, id=review_id)
    job = review.job
    package = review.recommendations or {}

    labor_min = Decimal(str(package.get("labor_hours_min") or 1))
    labor_max = Decimal(str(package.get("labor_hours_max") or labor_min))
    labor_hours = (labor_min + labor_max) / Decimal("2")
    labor_rate = Decimal("95.00")
    labor_total = labor_hours * labor_rate

    estimate = Estimate.objects.create(
        job=job,
        title=f"Estimate - {job.title}",
        status="draft",
        scope_of_work=package.get("customer_scope") or job.description or job.title,
        exclusions=(
            "Drywall repair, painting, permit fees, utility company charges, "
            "and hidden condition repairs are excluded unless specifically stated."
        ),
        terms=(
            "Estimate subject to field verification. Electrical code, permit, "
            "and equipment requirements must be verified before installation."
        ),
    )

    for item in job.job_materials.all():
        EstimateLineItem.objects.create(
            estimate=estimate,
            item_type="material",
            description=item.material.name,
            quantity=item.quantity,
            unit_price=item.material.sell_price or item.unit_cost,
            source_job_material=item,
        )

    EstimateLineItem.objects.create(
        estimate=estimate,
        item_type="labor",
        description=f"Labor - {package.get('scenario', 'Electrical Installation')} ({labor_hours} hrs)",
        quantity=Decimal("1"),
        unit_price=labor_total,
    )

    estimate.recalculate_totals()
    estimate.save()

    JobNote.objects.create(
        job=job,
        author="JARVIS",
        note=f"JARVIS generated estimate #{estimate.id} from job package.",
        internal=True,
    )

    messages.success(request, "Estimate created from JARVIS package.")
    return redirect("estimate_detail", estimate_id=estimate.id)