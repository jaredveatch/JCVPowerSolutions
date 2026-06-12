from decimal import Decimal
from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from .models import Job, Estimate, EstimateLineItem, Invoice


def money(value):
    return f"${Decimal(str(value or 0)):,.2f}"


def get_estimate_public_token(estimate):
    return signing.dumps(
        {"estimate_id": estimate.id},
        salt="jcv-estimate-approval",
    )


def get_estimate_from_token(token):
    try:
        data = signing.loads(
            token,
            salt="jcv-estimate-approval",
            max_age=60 * 60 * 24 * 60,
        )
        return Estimate.objects.get(id=data["estimate_id"])
    except Exception:
        raise Http404("Invalid or expired estimate link.")


def build_absolute_url(request, path):
    return request.build_absolute_uri(path)


def estimate_summary_totals(estimate):
    line_items = estimate.line_items.all()

    material_total = sum(
        (line.total for line in line_items if line.item_type == "material"),
        Decimal("0.00"),
    )

    labor_total = sum(
        (line.total for line in line_items if line.item_type == "labor"),
        Decimal("0.00"),
    )

    service_total = sum(
        (
            line.total
            for line in line_items
            if line.item_type in ["service", "fee"]
        ),
        Decimal("0.00"),
    )

    discount_total = sum(
        (line.total for line in line_items if line.item_type == "discount"),
        Decimal("0.00"),
    )

    # Fallback: if old estimates only have labor lines, keep the total honest.
    grouped_total = material_total + labor_total + service_total + discount_total

    if grouped_total <= 0 and estimate.subtotal:
        service_total = Decimal(str(estimate.subtotal or 0))

    return {
        "material_total": material_total,
        "labor_total": labor_total,
        "service_total": service_total,
        "discount_total": discount_total,
    }


@staff_member_required
def estimates(request):
    return render(request, "estimates.html", {
        "estimates": Estimate.objects.all().order_by("-created_at"),
    })


@staff_member_required
def create_estimate_from_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    estimate = Estimate.objects.create(
        job=job,
        title=f"Estimate - {job.title}",
        scope_of_work=job.description or "Electrical work as discussed during walkthrough.",
        subtotal=Decimal("0.00"),
        tax=Decimal("0.00"),
        total=Decimal("0.00"),
        status="draft",
        terms=(
            "Estimate valid for 30 days. Pricing subject to utility requirements, "
            "material availability, permits, and field conditions discovered during work."
        ),
    )

    material_total = Decimal("0.00")
    labor_total = Decimal("0.00")

    for item in job.job_materials.all():
        material_total += Decimal(str(item.material_sell_total or item.material_total or 0))
        labor_total += Decimal(str(item.labor_total or 0))

    if material_total > 0:
        EstimateLineItem.objects.create(
            estimate=estimate,
            item_type="material",
            description="Materials & Equipment",
            quantity=Decimal("1"),
            unit_price=material_total,
        )

    if labor_total > 0:
        EstimateLineItem.objects.create(
            estimate=estimate,
            item_type="labor",
            description="Labor & Installation",
            quantity=Decimal("1"),
            unit_price=labor_total,
        )

    estimate.subtotal = sum(
        (line.total for line in estimate.line_items.all()),
        Decimal("0.00"),
    )
    estimate.total = estimate.subtotal + estimate.tax
    estimate.save()

    job.status = "estimate_sent"
    job.save()

    return redirect(f"/estimates/{estimate.id}/")


@staff_member_required
def estimate_detail(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)
    token = get_estimate_public_token(estimate)

    return render(request, "estimate_detail.html", {
        "estimate": estimate,
        "line_items": estimate.line_items.all().order_by("item_type", "-total", "description"),
        "public_estimate_url": build_absolute_url(request, f"/estimates/public/{token}/"),
        "public_token": token,
        **estimate_summary_totals(estimate),
    })


def public_estimate_detail(request, token):
    estimate = get_estimate_from_token(token)
    summary = estimate_summary_totals(estimate)

    if request.method == "POST":
        customer_signature_name = request.POST.get("customer_signature_name", "").strip()
        accepted_terms = request.POST.get("accepted_terms")

        if customer_signature_name and accepted_terms:
            estimate.customer_signature_name = customer_signature_name
            estimate.accepted_terms = True
            estimate.signed_date = timezone.now()
            estimate.status = "approved"
            estimate.save()

            job = estimate.job
            job.status = "approved"
            job.save()

            Invoice.objects.get_or_create(
                estimate=estimate,
                defaults={
                    "job": job,
                    "title": f"Invoice - {job.title}",
                    "description": estimate.scope_of_work,
                    "subtotal": estimate.subtotal,
                    "tax": estimate.tax,
                    "total": estimate.total,
                    "amount_due": estimate.total,
                    "amount_paid": Decimal("0.00"),
                    "status": "draft",
                    "due_date": timezone.now().date(),
                },
            )

            return redirect(f"/estimates/public/{token}/?signed=1")

        return render(request, "public_estimate_detail.html", {
            "estimate": estimate,
            "error": "Please enter your full name and agree to the terms.",
            **summary,
        })

    return render(request, "public_estimate_detail.html", {
        "estimate": estimate,
        **summary,
    })


@staff_member_required
def estimate_pdf(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)
    summary = estimate_summary_totals(estimate)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left = 0.65 * inch
    right = width - 0.65 * inch
    top = height - 0.65 * inch

    gold = (0.95, 0.75, 0.22)
    dark = (0.08, 0.08, 0.08)
    gray = (0.35, 0.35, 0.35)
    light_gray = (0.85, 0.85, 0.85)

    y = top

    def wrapped_lines(text, limit=92):
        words = str(text or "").split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()

            if len(test) <= limit:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [""]

    def new_page():
        pdf.showPage()
        return top

    def check_page(current_y, needed=1.5 * inch):
        if current_y < needed:
            return new_page()
        return current_y

    def section_header(title, current_y):
        pdf.setStrokeColorRGB(*gold)
        pdf.setLineWidth(2)
        pdf.line(left, current_y - 0.08 * inch, right, current_y - 0.08 * inch)

        pdf.setFillColorRGB(*dark)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(left, current_y, title)

        return current_y - 0.35 * inch

    # Header
    pdf.setFillColorRGB(*dark)
    pdf.rect(0, height - 1.55 * inch, width, 1.55 * inch, stroke=0, fill=1)

    pdf.setFillColorRGB(*gold)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(left, height - 0.70 * inch, "JCV Power Solutions")

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, height - 1.00 * inch, "Professional Electrical Services")

    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawRightString(right, height - 0.70 * inch, "CUSTOMER ESTIMATE")

    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(right, height - 1.00 * inch, f"Estimate #{estimate.id}")

    y = height - 1.95 * inch

    # Customer/project box
    info_height = 1.45 * inch
    pdf.setStrokeColorRGB(*light_gray)
    pdf.roundRect(left, y - info_height, right - left, info_height, 10, stroke=1, fill=0)

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 0.22 * inch, y - 0.32 * inch, "CUSTOMER")

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left + 0.22 * inch, y - 0.58 * inch, estimate.job.customer.name[:40])

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 3.70 * inch, y - 0.32 * inch, "PROJECT")

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left + 3.70 * inch, y - 0.58 * inch, estimate.job.title[:42])

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 0.22 * inch, y - 1.00 * inch, "DATE")

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left + 0.90 * inch, y - 1.00 * inch, estimate.created_at.strftime("%m/%d/%Y"))

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 3.70 * inch, y - 1.00 * inch, "STATUS")

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left + 4.45 * inch, y - 1.00 * inch, estimate.status.title())

    y -= info_height + 0.45 * inch

    # Scope
    y = section_header("Scope of Work", y)
    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)

    for line in wrapped_lines(estimate.scope_of_work or "Electrical work as discussed.", 96):
        y = check_page(y)
        pdf.drawString(left + 0.10 * inch, y, line)
        y -= 0.22 * inch

    y -= 0.15 * inch

    # Simplified project breakdown
    y = check_page(y, 2.4 * inch)
    y = section_header("Project Breakdown", y)

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left + 0.10 * inch, y, "Description")
    pdf.drawRightString(right, y, "Total")
    y -= 0.22 * inch

    pdf.setStrokeColorRGB(*light_gray)
    pdf.line(left, y, right, y)
    y -= 0.22 * inch

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)

    rows = [
        ("Materials & Equipment", summary["material_total"]),
        ("Labor & Installation", summary["labor_total"]),
    ]

    if summary["service_total"]:
        rows.append(("Permits / Fees / Other", summary["service_total"]))

    if estimate.tax:
        rows.append(("Tax", estimate.tax))

    for label, amount in rows:
        y = check_page(y)
        pdf.drawString(left + 0.10 * inch, y, label)
        pdf.drawRightString(right, y, money(amount))
        y -= 0.25 * inch

    y -= 0.20 * inch

    if estimate.exclusions:
        y = check_page(y, 2 * inch)
        y = section_header("Exclusions", y)

        pdf.setFillColorRGB(*gray)
        pdf.setFont("Helvetica", 9)

        for line in wrapped_lines(estimate.exclusions, 102):
            y = check_page(y)
            pdf.drawString(left + 0.10 * inch, y, line)
            y -= 0.18 * inch

        y -= 0.18 * inch

    # Total box
    y = check_page(y, 2.5 * inch)

    total_box_width = 3.05 * inch
    total_box_height = 1.15 * inch
    total_x = right - total_box_width

    pdf.setFillColorRGB(*dark)
    pdf.roundRect(total_x, y - total_box_height, total_box_width, total_box_height, 10, stroke=0, fill=1)

    pdf.setFillColorRGB(*gold)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(total_x + 0.25 * inch, y - 0.34 * inch, "PROJECT TOTAL")

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(total_x + 0.25 * inch, y - 0.78 * inch, money(estimate.total))

    y -= total_box_height + 0.55 * inch

    # Terms
    y = check_page(y, 2 * inch)
    y = section_header("Terms & Conditions", y)

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica", 9)

    terms = estimate.terms or (
        "Estimate valid for 30 days. Pricing subject to utility requirements, "
        "material availability, permits, and field conditions discovered during work."
    )

    for line in wrapped_lines(terms, 104):
        y = check_page(y)
        pdf.drawString(left + 0.10 * inch, y, line)
        y -= 0.18 * inch

    y -= 0.55 * inch

    # Approval
    y = check_page(y, 1.8 * inch)

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "Customer Approval")

    y -= 0.35 * inch

    if estimate.accepted_terms and estimate.customer_signature_name:
        pdf.setFillColorRGB(*dark)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(left, y, f"Electronically Signed By: {estimate.customer_signature_name}")

        y -= 0.24 * inch

        pdf.setFillColorRGB(*gray)
        pdf.setFont("Helvetica", 9)
        signed_date = estimate.signed_date.strftime("%m/%d/%Y %I:%M %p") if estimate.signed_date else ""
        pdf.drawString(left, y, f"Signed Date: {signed_date}")
        y -= 0.24 * inch
        pdf.drawString(left, y, "Customer approved this estimate electronically.")
    else:
        pdf.setFillColorRGB(*gray)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(left, y, "Pending customer approval. Customer may approve using the secure online estimate link.")

    # Footer
    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        width / 2,
        0.40 * inch,
        "JCV Power Solutions • Professional Electrical Services",
    )

    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"estimate-{estimate.id}.pdf",
    )


@staff_member_required
def edit_estimate(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

    if request.method == "POST":
        estimate.title = request.POST.get("title")
        estimate.scope_of_work = request.POST.get("scope_of_work")
        estimate.exclusions = request.POST.get("exclusions")
        estimate.terms = request.POST.get("terms")

        subtotal = request.POST.get("subtotal", "").strip()
        tax = request.POST.get("tax", "").strip()

        estimate.subtotal = Decimal(subtotal) if subtotal else Decimal("0.00")
        estimate.tax = Decimal(tax) if tax else Decimal("0.00")
        estimate.total = estimate.subtotal + estimate.tax
        estimate.save()

        return redirect(f"/estimates/{estimate.id}/")

    return render(request, "edit_estimate.html", {
        "estimate": estimate,
        "line_items": estimate.line_items.all().order_by("item_type", "-total", "description"),
    })


@staff_member_required
def approve_estimate(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

    estimate.status = "approved"
    estimate.accepted_terms = True
    estimate.signed_date = timezone.now()

    if not estimate.customer_signature_name:
        estimate.customer_signature_name = "Approved by JCV Admin"

    estimate.save()

    job = estimate.job
    job.status = "approved"
    job.save()

    invoice, created = Invoice.objects.get_or_create(
        estimate=estimate,
        defaults={
            "job": job,
            "title": f"Invoice - {job.title}",
            "description": estimate.scope_of_work,
            "subtotal": estimate.subtotal,
            "tax": estimate.tax,
            "total": estimate.total,
            "amount_due": estimate.total,
            "amount_paid": Decimal("0.00"),
            "status": "draft",
            "due_date": timezone.now().date(),
        },
    )

    if not invoice.job:
        invoice.job = job

    invoice.title = invoice.title or f"Invoice - {job.title}"
    invoice.description = invoice.description or estimate.scope_of_work
    invoice.subtotal = estimate.subtotal
    invoice.tax = estimate.tax
    invoice.total = estimate.total
    invoice.amount_due = estimate.total - invoice.amount_paid

    if invoice.amount_paid <= 0:
        invoice.status = "draft"

    invoice.save()

    return redirect(f"/invoices/{invoice.id}/")


@staff_member_required
def delete_estimate(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)
    job_id = estimate.job.id

    if request.method == "POST":
        estimate.delete()
        return redirect(f"/jobs/{job_id}/")

    return redirect(f"/estimates/{estimate.id}/")