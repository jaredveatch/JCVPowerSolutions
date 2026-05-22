from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    Job,
    Estimate,
    Invoice,
)


def home(request):
    if request.method == "POST":

        if "quote_form" in request.POST:
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            service = request.POST.get("service", "").strip()
            message = request.POST.get("message", "").strip()

            if not name or not phone or not email or not service or not message:
                return JsonResponse({
                    "success": False,
                    "message": "Please fill out all quote request fields."
                }, status=400)

            QuoteRequest.objects.create(
                name=name,
                phone=phone,
                email=email,
                service=service,
                message=message,
            )

            return JsonResponse({
                "success": True,
                "message": "Thank you for submitting your request. We will contact you soon."
            })

        if "career_form" in request.POST:
            name = request.POST.get("applicant_name", "").strip()
            phone = request.POST.get("applicant_phone", "").strip()
            email = request.POST.get("applicant_email", "").strip()
            position = request.POST.get("position", "").strip()
            experience = request.POST.get("experience", "").strip()
            license_info = request.POST.get("license", "").strip()
            message = request.POST.get("career_message", "").strip()

            if not name or not phone or not email or not position:
                return JsonResponse({
                    "success": False,
                    "message": "Please fill out all required career application fields."
                }, status=400)

            CareerApplication.objects.create(
                name=name,
                phone=phone,
                email=email,
                position=position,
                experience=experience,
                license_info=license_info,
                message=message,
            )

            return JsonResponse({
                "success": True,
                "message": "Thank you for submitting your application. We will review it soon."
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid form submission."
        }, status=400)

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
    context = {
        "leads": QuoteRequest.objects.order_by("-created_at"),
    }

    return render(request, "leads.html", context)


@staff_member_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)

    context = {
        "lead": lead,
    }

    return render(request, "lead_detail.html", context)


@staff_member_required
def convert_lead(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)

    customer = Customer.objects.create(
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
    )

    return redirect(f"/customers/{customer.id}/")


@staff_member_required
def customers(request):
    context = {
        "customers": Customer.objects.all().order_by("-id"),
    }

    return render(request, "customers.html", context)


@staff_member_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    context = {
        "customer": customer,
        "jobs_count": Job.objects.count(),
        "estimates_count": Estimate.objects.count(),
        "invoices_count": Invoice.objects.count(),
    }

    return render(request, "customer_detail.html", context)
@staff_member_required
def delete_customer(request, customer_id):

    customer = get_object_or_404(Customer, id=customer_id)

    customer.delete()

    return redirect("/customers/")