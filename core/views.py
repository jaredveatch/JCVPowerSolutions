from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

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
    return render(request, "dashboard.html", {
        "new_quotes": QuoteRequest.objects.order_by("-created_at")[:5],
        "recent_jobs": Job.objects.order_by("-created_at")[:5],
        "recent_tasks": Task.objects.filter(status="open").order_by("due_date")[:5],
        "quotes_count": QuoteRequest.objects.count(),
        "customers_count": Customer.objects.count(),
        "jobs_count": Job.objects.count(),
        "estimates_count": Estimate.objects.count(),
        "invoices_count": Invoice.objects.count(),
        "open_tasks_count": Task.objects.filter(status="open").count(),
    })


@staff_member_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    customers = []
    jobs = []
    invoices = []

    if query:
        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(job_address__icontains=query) |
            Q(description__icontains=query)
        )

        invoices = Invoice.objects.filter(
            Q(invoice_number__icontains=query) |
            Q(title__icontains=query)
        )

    return render(request, "search_results.html", {
        "query": query,
        "customers": customers,
        "jobs": jobs,
        "invoices": invoices,
    })