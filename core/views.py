from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    Job,
    Estimate,
    Invoice,
    Task,
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
        # Main dashboard lists
        "new_quotes": recent_leads,
        "recent_leads": recent_leads,
        "recent_jobs": Job.objects.order_by("-created_at")[:5],
        "recent_tasks": open_tasks.order_by("due_date", "-created_at")[:5],
        "jobs_needing_quotes": jobs_needing_quotes,
        "approved_jobs": approved_jobs,
        "overdue_invoices": overdue_invoices.order_by("due_date")[:5],

        # Main counters
        "quotes_count": new_quotes.count(),
        "customers_count": Customer.objects.count(),
        "jobs_count": active_jobs.count(),
        "estimates_count": pending_estimates.count(),
        "invoices_count": open_invoices.count(),
        "open_tasks_count": open_tasks.count(),

        # Extra KPI counters
        "total_jobs_count": Job.objects.count(),
        "total_estimates_count": Estimate.objects.count(),
        "total_invoices_count": Invoice.objects.count(),
        "jobs_needing_quotes_count": jobs_needing_quotes.count(),
        "approved_jobs_count": approved_jobs.count(),
        "overdue_invoices_count": overdue_invoices.count(),

        # Money KPIs
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