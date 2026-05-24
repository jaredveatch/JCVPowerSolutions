from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

from .models import QuoteRequest, Customer


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
        status="active",
    )

    lead.status = "converted"
    lead.save()

    return redirect(f"/customers/{customer.id}/")


@staff_member_required
def delete_lead(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)

    if request.method == "POST":
        lead.delete()
        return redirect("/leads/")

    return redirect(f"/leads/{lead.id}/")


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
            existing_customer = Customer.objects.filter(phone=phone).first()

            if existing_customer:
                return redirect(f"/customers/{existing_customer.id}/")

            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                status="active",
            )

            return redirect(f"/customers/{customer.id}/")

    return redirect("/customers/")


@staff_member_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    return render(request, "customer_detail.html", {
        "customer": customer,
        "jobs": customer.jobs.all().order_by("-created_at"),
        "tasks": customer.tasks.all().order_by("-created_at"),
    })


@staff_member_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.company_name = request.POST.get("company_name")
        customer.phone = request.POST.get("phone")
        customer.email = request.POST.get("email")
        customer.address = request.POST.get("address")
        customer.city = request.POST.get("city")
        customer.notes = request.POST.get("notes")
        customer.status = request.POST.get("status")
        customer.save()

        return redirect(f"/customers/{customer.id}/")

    return render(request, "edit_customer.html", {
        "customer": customer,
    })


@staff_member_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.delete()
        return redirect("/customers/")

    return redirect(f"/customers/{customer.id}/")