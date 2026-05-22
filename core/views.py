from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.dateparse import parse_datetime

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    ServiceTemplate,
    Job,
    Estimate,
    Invoice,
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
                "message": "Thank you for submitting your request. We will contact you soon."
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
                "message": "Thank you for submitting your application. We will review it soon."
            })

    return render(request, "home.html", {})


@staff_member_required
def dashboard(request):
    context = {
        "new_quotes": QuoteRequest.objects.order_by("-created_at")[:5],
        "recent_jobs": Job.objects.order_by("-created_at")[:5],
        "quotes_count": QuoteRequest.objects.count(),
        "customers_count": Customer.objects.count(),
        "jobs_count": Job.objects.count(),
        "estimates_count": Estimate.objects.count(),
        "invoices_count": Invoice.objects.count(),
    }

    return render(request, "dashboard.html", context)


@staff_member_required
def leads(request):
    return render(request, "leads.html", {
        "leads": QuoteRequest.objects.order_by("-created_at"),
    })


@staff_member_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)

    return render(request, "lead_detail.html", {
        "lead": lead,
    })


@staff_member_required
def convert_lead(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)

    customer = Customer.objects.create(
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        notes=lead.message,
    )

    return redirect(f"/customers/{customer.id}/")


@staff_member_required
def customers(request):
    return render(request, "customers.html", {
        "customers": Customer.objects.all().order_by("-id"),
    })


@staff_member_required
def create_customer(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()

        if name and phone:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
            )

            return redirect(f"/customers/{customer.id}/")

    return redirect("/customers/")


@staff_member_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    return render(request, "customer_detail.html", {
        "customer": customer,
        "jobs": customer.jobs.all().order_by("-created_at"),
    })


@staff_member_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.delete()
        return redirect("/customers/")

    return redirect(f"/customers/{customer.id}/")


@staff_member_required
def create_job(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    templates = ServiceTemplate.objects.filter(active=True).order_by("category", "name")

    if request.method == "POST":
        template_id = request.POST.get("template")
        template = None

        if template_id:
            template = ServiceTemplate.objects.filter(id=template_id).first()

        title = request.POST.get("title", "").strip()
        status = request.POST.get("status", "site_visit")
        job_address = request.POST.get("job_address", "").strip()
        description = request.POST.get("description", "").strip()
        site_notes = request.POST.get("site_notes", "").strip()
        material_notes = request.POST.get("material_notes", "").strip()
        scheduled_date_raw = request.POST.get("scheduled_date", "").strip()

        scheduled_date = None
        if scheduled_date_raw:
            scheduled_date = parse_datetime(scheduled_date_raw)

        estimated_total_price = None
        price_raw = request.POST.get("estimated_total_price", "").strip()

        if price_raw:
            estimated_total_price = Decimal(price_raw)
        elif template:
            estimated_total_price = template.default_price

        if not title and template:
            title = template.name

        if not description and template:
            description = template.customer_description

        if not material_notes and template:
            material_notes = template.internal_checklist

        job = Job.objects.create(
            customer=customer,
            template=template,
            title=title or "New Job",
            status=status,
            job_address=job_address or customer.address,
            description=description,
            site_notes=site_notes,
            material_notes=material_notes,
            estimated_total_price=estimated_total_price,
            scheduled_date=scheduled_date,
        )

        return redirect(f"/jobs/{job.id}/")

    return render(request, "create_job.html", {
        "customer": customer,
        "templates": templates,
    })


@staff_member_required
def jobs(request):
    return render(request, "jobs.html", {
        "jobs": Job.objects.all().order_by("-created_at"),
    })


@staff_member_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(request, "job_detail.html", {
        "job": job,
        "estimates": job.estimates.all().order_by("-created_at"),
    })


@staff_member_required
def create_estimate_from_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    scope = job.description or "Electrical work as discussed during site visit."
    subtotal = job.estimated_total_price or Decimal("0.00")

    estimate = Estimate.objects.create(
        job=job,
        title=f"Estimate - {job.title}",
        scope_of_work=scope,
        subtotal=subtotal,
        tax=Decimal("0.00"),
        total=subtotal,
        status="draft",
    )

    job.status = "estimate_needed"
    job.save()

    return redirect(f"/admin/core/estimate/{estimate.id}/change/")