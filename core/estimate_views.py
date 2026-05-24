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

    left = 0.55 * inch
    right = width - 0.55 * inch
    page_width = right - left

    black = (0.055, 0.055, 0.055)
    gold = (0.95, 0.72, 0.16)
    dark_gray = (0.18, 0.18, 0.18)
    mid_gray = (0.48, 0.48, 0.48)
    light_gray = (0.88, 0.88, 0.88)
    soft_gray = (0.97, 0.97, 0.97)
    white = (1, 1, 1)

    def fill(color):
        pdf.setFillColorRGB(*color)

    def stroke(color):
        pdf.setStrokeColorRGB(*color)

    def money(value):
        return f"${Decimal(str(value or 0)):,.2f}"

    def wrap_text(text, max_chars=76):
        words = str(text or "").split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()

            if len(test) <= max_chars:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [""]

    def card(x, y_top, w, h, fill_color=white, radius=9):
        fill(fill_color)
        stroke(light_gray)
        pdf.setLineWidth(0.8)
        pdf.roundRect(
            x,
            y_top - h,
            w,
            h,
            radius,
            stroke=1,
            fill=1,
        )

    def label(text, x, y):
        fill(gold)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(x, y, text)

    # =====================================================
    # HEADER
    # =====================================================

    header_h = 1.08 * inch

    fill(black)
    pdf.rect(
        0,
        height - header_h,
        width,
        header_h,
        stroke=0,
        fill=1,
    )

    fill(gold)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(left, height - 0.46 * inch, "JCV Power Solutions")

    fill(white)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(left, height - 0.72 * inch, "Professional Electrical Services")

    fill(white)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(right, height - 0.46 * inch, "ESTIMATE")

    fill((0.78, 0.78, 0.78))
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(right, height - 0.72 * inch, f"Estimate #{estimate.id}")

    # =====================================================
    # TITLE
    # =====================================================

    y = height - 1.45 * inch

    fill(black)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, y, "Electrical Service Proposal")

    y -= 0.22 * inch

    fill(mid_gray)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(width / 2, y, "Prepared for your review and approval")

    y -= 0.34 * inch

    # =====================================================
    # INFO CARDS
    # =====================================================

    gap = 0.16 * inch
    small_card_w = (page_width - gap) / 2
    small_card_h = 0.86 * inch

    card(left, y, small_card_w, small_card_h, soft_gray)
    card(left + small_card_w + gap, y, small_card_w, small_card_h, soft_gray)

    label("CUSTOMER", left + 0.16 * inch, y - 0.22 * inch)
    label("PROJECT", left + small_card_w + gap + 0.16 * inch, y - 0.22 * inch)

    fill(black)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 0.16 * inch, y - 0.47 * inch, estimate.job.customer.name[:34])

    project_lines = wrap_text(estimate.job.title, 31)
    project_y = y - 0.43 * inch

    pdf.setFont("Helvetica-Bold", 9.5)
    for line in project_lines[:2]:
        pdf.drawString(left + small_card_w + gap + 0.16 * inch, project_y, line)
        project_y -= 0.15 * inch

    fill(mid_gray)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(left + 0.16 * inch, y - 0.70 * inch, f"Date: {estimate.created_at.strftime('%m/%d/%Y')}")
    pdf.drawString(
        left + small_card_w + gap + 0.16 * inch,
        y - 0.70 * inch,
        f"Status: {estimate.status.title()}",
    )

    y -= small_card_h + 0.24 * inch

    # =====================================================
    # SCOPE CARD
    # =====================================================

    scope = estimate.scope_of_work or "Electrical work as discussed."
    scope_lines = wrap_text(scope, 88)

    max_scope_lines = 4
    visible_scope_lines = scope_lines[:max_scope_lines]

    scope_card_h = 1.35 * inch

    card(left, y, page_width, scope_card_h, white)

    label("SCOPE OF WORK", left + 0.18 * inch, y - 0.23 * inch)

    fill(black)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(left + 0.18 * inch, y - 0.47 * inch, "Project Overview")

    fill(dark_gray)
    pdf.setFont("Helvetica", 9)

    text_y = y - 0.72 * inch

    for line in visible_scope_lines:
        pdf.drawString(left + 0.28 * inch, text_y, f"• {line}")
        text_y -= 0.17 * inch

    y -= scope_card_h + 0.22 * inch

    # =====================================================
    # TOTAL CARD
    # =====================================================

    total_h = 1.18 * inch

    fill(black)
    pdf.roundRect(
        left,
        y - total_h,
        page_width,
        total_h,
        14,
        stroke=0,
        fill=1,
    )

    fill(gold)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(width / 2, y - 0.30 * inch, "PROJECT TOTAL")

    fill(white)
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, y - 0.76 * inch, money(estimate.total))

    fill((0.78, 0.78, 0.78))
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(
        width / 2,
        y - 1.02 * inch,
        "Includes approved scope, standard labor, and listed project pricing.",
    )

    y -= total_h + 0.24 * inch

    # =====================================================
    # TERMS CARD
    # =====================================================

    terms = estimate.terms or (
        "Estimate valid for 30 days. Pricing is subject to utility requirements, "
        "material availability, permits, and field conditions discovered during work."
    )

    terms_lines = wrap_text(terms, 92)[:3]

    terms_h = 0.95 * inch

    card(left, y, page_width, terms_h, soft_gray)

    label("TERMS", left + 0.18 * inch, y - 0.22 * inch)

    fill(dark_gray)
    pdf.setFont("Helvetica", 8.5)

    terms_y = y - 0.45 * inch

    for line in terms_lines:
        pdf.drawString(left + 0.18 * inch, terms_y, line)
        terms_y -= 0.15 * inch

    y -= terms_h + 0.22 * inch

    # =====================================================
    # ACCEPTANCE CARD
    # =====================================================

    accept_h = 0.98 * inch

    card(left, y, page_width, accept_h, white)

    fill(black)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left + 0.18 * inch, y - 0.25 * inch, "Acceptance")

    fill(mid_gray)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(
        left + 0.18 * inch,
        y - 0.43 * inch,
        "By signing below, customer authorizes JCV Power Solutions to proceed with the approved scope.",
    )

    line_y = y - 0.72 * inch

    stroke(black)
    pdf.setLineWidth(0.8)
    pdf.line(left + 0.18 * inch, line_y, left + 3.30 * inch, line_y)
    pdf.line(right - 2.20 * inch, line_y, right - 0.18 * inch, line_y)

    fill(mid_gray)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(left + 0.18 * inch, line_y - 0.13 * inch, "Customer Signature")
    pdf.drawString(right - 2.20 * inch, line_y - 0.13 * inch, "Date")

    # =====================================================
    # FOOTER
    # =====================================================

    stroke(light_gray)
    pdf.setLineWidth(0.7)
    pdf.line(left, 0.55 * inch, right, 0.55 * inch)

    fill(mid_gray)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(
        width / 2,
        0.36 * inch,
        "JCV Power Solutions • Professional Electrical Services • jcvpowersolutions.com",
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