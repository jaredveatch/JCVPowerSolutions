from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from .models import (
    Job,
    Invoice,
    Payment,
)


@staff_member_required
def invoices(request):
    return render(request, "invoices.html", {
        "invoices": Invoice.objects.all().order_by("-created_at"),
    })


@staff_member_required
def create_invoice_from_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    subtotal = (
        job.installed_total()
        or job.estimated_total_price
        or Decimal("0.00")
    )

    invoice = Invoice.objects.create(
        job=job,
        title=f"Invoice - {job.title}",
        description=job.description,
        subtotal=subtotal,
        tax=Decimal("0.00"),
        total=subtotal,
        due_date=timezone.now().date(),
        status="sent",
    )

    return redirect(f"/invoices/{invoice.id}/")


@staff_member_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    return render(request, "invoice_detail.html", {
        "invoice": invoice,
        "payments": invoice.payments.all().order_by("-paid_at"),
    })


@staff_member_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        invoice.title = request.POST.get("title")
        invoice.description = request.POST.get("description")
        invoice.status = request.POST.get("status")

        subtotal = request.POST.get("subtotal", "").strip()
        tax = request.POST.get("tax", "").strip()

        invoice.subtotal = Decimal(subtotal) if subtotal else Decimal("0.00")
        invoice.tax = Decimal(tax) if tax else Decimal("0.00")
        invoice.total = invoice.subtotal + invoice.tax
        invoice.amount_due = invoice.total - invoice.amount_paid
        invoice.save()

        return redirect(f"/invoices/{invoice.id}/")

    return render(request, "edit_invoice.html", {
        "invoice": invoice,
    })


@staff_member_required
def add_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        amount = request.POST.get("amount")

        if amount:
            Payment.objects.create(
                invoice=invoice,
                amount=Decimal(amount),
                method=request.POST.get("method", "card"),
                reference=request.POST.get("reference", ""),
                notes=request.POST.get("notes", ""),
            )

    return redirect(f"/invoices/{invoice.id}/")