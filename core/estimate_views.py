from decimal import Decimal
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from .models import (
    Job,
    Estimate,
    EstimateLineItem,
    Invoice,
)


@staff_member_required
def estimates(request):
    return render(request, "estimates.html", {
        "estimates": Estimate.objects.all().order_by("-created_at"),
    })


@staff_member_required
def create_estimate_from_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    scope = job.description or "Electrical work as discussed during walkthrough."

    estimate = Estimate.objects.create(
        job=job,
        title=f"Estimate - {job.title}",
        scope_of_work=scope,
        subtotal=Decimal("0.00"),
        tax=Decimal("0.00"),
        total=Decimal("0.00"),
        status="draft",
    )

    for item in job.job_materials.all().order_by(
        "-total_cost",
        "-labor_total",
        "-material_total",
        "material__name",
    ):
        material_name = item.material.name if item.material else "Material"

        if item.material_total and item.material_total > 0:
            EstimateLineItem.objects.create(
                estimate=estimate,
                item_type="material",
                description=material_name,
                quantity=item.quantity,
                unit_price=item.unit_cost,
                source_job_material=item,
            )

        if item.labor_total and item.labor_total > 0:
            EstimateLineItem.objects.create(
                estimate=estimate,
                item_type="labor",
                description=f"Labor - {material_name}",
                quantity=Decimal("1"),
                unit_price=item.labor_total,
                source_job_material=item,
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

    return render(request, "estimate_detail.html", {
        "estimate": estimate,
        "line_items": estimate.line_items.all().order_by(
            "item_type",
            "-total",
            "description",
        ),
    })


@staff_member_required
def estimate_pdf(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

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

    def money(value):
        return f"${Decimal(str(value or 0)):,.2f}"

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

        pdf.line(
            left,
            current_y - 0.08 * inch,
            right,
            current_y - 0.08 * inch,
        )

        pdf.setFillColorRGB(*dark)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(left, current_y, title)

        return current_y - 0.35 * inch

    # =====================================================
    # HEADER
    # =====================================================

    pdf.setFillColorRGB(*dark)

    pdf.rect(
        0,
        height - 1.55 * inch,
        width,
        1.55 * inch,
        stroke=0,
        fill=1,
    )

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

    # =====================================================
    # CUSTOMER / PROJECT BOX
    # =====================================================

    info_height = 1.45 * inch

    pdf.setStrokeColorRGB(*light_gray)

    pdf.roundRect(
        left,
        y - info_height,
        right - left,
        info_height,
        10,
        stroke=1,
        fill=0,
    )

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
    pdf.drawString(
        left + 0.90 * inch,
        y - 1.00 * inch,
        estimate.created_at.strftime("%m/%d/%Y"),
    )

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 3.70 * inch, y - 1.00 * inch, "STATUS")

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left + 4.45 * inch, y - 1.00 * inch, estimate.status.title())

    y -= info_height + 0.45 * inch

    # =====================================================
    # SCOPE
    # =====================================================

    y = section_header("Scope of Work", y)

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica", 10)

    scope = estimate.scope_of_work or "Electrical work as discussed."

    for line in wrapped_lines(scope, 96):
        y = check_page(y)

        pdf.drawString(
            left + 0.10 * inch,
            y,
            line,
        )

        y -= 0.22 * inch

    y -= 0.15 * inch

    # =====================================================
    # EXCLUSIONS
    # =====================================================

    if estimate.exclusions:
        y = check_page(y, 2 * inch)
        y = section_header("Exclusions", y)

        pdf.setFillColorRGB(*gray)
        pdf.setFont("Helvetica", 9)

        for line in wrapped_lines(estimate.exclusions, 102):
            y = check_page(y)

            pdf.drawString(
                left + 0.10 * inch,
                y,
                line,
            )

            y -= 0.18 * inch

        y -= 0.18 * inch

    # =====================================================
    # TOTAL
    # =====================================================

    y = check_page(y, 2.5 * inch)

    total_box_width = 3.05 * inch
    total_box_height = 1.15 * inch
    total_x = right - total_box_width

    pdf.setFillColorRGB(*dark)

    pdf.roundRect(
        total_x,
        y - total_box_height,
        total_box_width,
        total_box_height,
        10,
        stroke=0,
        fill=1,
    )

    pdf.setFillColorRGB(*gold)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(total_x + 0.25 * inch, y - 0.34 * inch, "PROJECT TOTAL")

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(total_x + 0.25 * inch, y - 0.78 * inch, money(estimate.total))

    y -= total_box_height + 0.55 * inch

    # =====================================================
    # TERMS
    # =====================================================

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

        pdf.drawString(
            left + 0.10 * inch,
            y,
            line,
        )

        y -= 0.18 * inch

    y -= 0.55 * inch

    # =====================================================
    # SIGNATURE
    # =====================================================

    y = check_page(y, 1.8 * inch)

    pdf.setFillColorRGB(*dark)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "Accepted By Signing Below")

    y -= 0.50 * inch

    pdf.setStrokeColorRGB(*dark)

    pdf.line(
        left,
        y,
        left + 3.10 * inch,
        y,
    )

    pdf.line(
        right - 2.40 * inch,
        y,
        right,
        y,
    )

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(left, y - 0.18 * inch, "Customer Signature")
    pdf.drawString(right - 2.40 * inch, y - 0.18 * inch, "Date")

    # =====================================================
    # FOOTER
    # =====================================================

    pdf.setFillColorRGB(*gray)
    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        width / 2,
        0.40 * inch,
        "JCV Power Solutions • Professional Electrical Services",
    )

    pdf.save()
    buffer.seek(0)

    filename = f"estimate-{estimate.id}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
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
        "line_items": estimate.line_items.all().order_by(
            "item_type",
            "-total",
            "description",
        ),
    })


@staff_member_required
def approve_estimate(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

    estimate.status = "approved"
    estimate.accepted_terms = True
    estimate.signed_date = timezone.now()
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