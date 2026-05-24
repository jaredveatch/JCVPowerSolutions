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
    page_width = right - left

    black = (0.06, 0.06, 0.06)
    gold = (0.95, 0.72, 0.16)
    dark_gray = (0.22, 0.22, 0.22)
    mid_gray = (0.48, 0.48, 0.48)
    light_gray = (0.91, 0.91, 0.91)
    soft_gray = (0.97, 0.97, 0.97)

    def set_fill(color):
        pdf.setFillColorRGB(*color)

    def set_stroke(color):
        pdf.setStrokeColorRGB(*color)

    def money(value):
        return f"${Decimal(str(value or 0)):,.2f}"

    def wrap_text(text, max_chars=82):
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

    def draw_card(x, y_top, w, h, fill=soft_gray):
        set_fill(fill)
        set_stroke(light_gray)

        pdf.roundRect(
            x,
            y_top - h,
            w,
            h,
            10,
            stroke=1,
            fill=1,
        )

    def draw_footer():
        set_stroke(light_gray)
        pdf.line(left, 0.72 * inch, right, 0.72 * inch)

        set_fill(mid_gray)
        pdf.setFont("Helvetica", 8)

        pdf.drawCentredString(
            width / 2,
            0.48 * inch,
            "JCV Power Solutions • Professional Electrical Services • jcvpowersolutions.com",
        )

    def new_page():
        pdf.showPage()
        draw_footer()
        return height - 0.85 * inch

    def check_page(y, needed=1.4 * inch):
        if y < needed:
            return new_page()

        return y

    # =====================================================
    # HEADER
    # =====================================================

    set_fill(black)
    pdf.rect(
        0,
        height - 1.35 * inch,
        width,
        1.35 * inch,
        stroke=0,
        fill=1,
    )

    set_fill(gold)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(left, height - 0.62 * inch, "JCV Power Solutions")

    set_fill((1, 1, 1))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left, height - 0.90 * inch, "Professional Electrical Services")

    set_fill((1, 1, 1))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(right, height - 0.62 * inch, "ESTIMATE")

    set_fill((0.78, 0.78, 0.78))
    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(right, height - 0.90 * inch, f"Estimate #{estimate.id}")

    # =====================================================
    # TITLE
    # =====================================================

    y = height - 1.85 * inch

    set_fill(black)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, y, "Electrical Service Proposal")

    y -= 0.28 * inch

    set_fill(mid_gray)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        width / 2,
        y,
        "Prepared for your review and approval",
    )

    y -= 0.48 * inch

    # =====================================================
    # CUSTOMER / PROJECT CARDS
    # =====================================================

    card_gap = 0.20 * inch
    card_width = (page_width - card_gap) / 2
    card_height = 1.18 * inch

    draw_card(left, y, card_width, card_height)
    draw_card(left + card_width + card_gap, y, card_width, card_height)

    set_fill(mid_gray)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(left + 0.18 * inch, y - 0.28 * inch, "CUSTOMER")
    pdf.drawString(left + card_width + card_gap + 0.18 * inch, y - 0.28 * inch, "PROJECT")

    set_fill(black)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left + 0.18 * inch, y - 0.56 * inch, estimate.job.customer.name[:38])

    project_lines = wrap_text(estimate.job.title, 34)

    pdf.setFont("Helvetica-Bold", 10)
    project_y = y - 0.54 * inch

    for line in project_lines[:2]:
        pdf.drawString(
            left + card_width + card_gap + 0.18 * inch,
            project_y,
            line,
        )
        project_y -= 0.18 * inch

    set_fill(mid_gray)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(left + 0.18 * inch, y - 0.92 * inch, f"Date: {estimate.created_at.strftime('%m/%d/%Y')}")
    pdf.drawString(
        left + card_width + card_gap + 0.18 * inch,
        y - 0.92 * inch,
        f"Status: {estimate.status.title()}",
    )

    y -= card_height + 0.42 * inch

    # =====================================================
    # SCOPE CARD
    # =====================================================

    scope = estimate.scope_of_work or "Electrical work as discussed."

    scope_lines = wrap_text(scope, 88)
    scope_height = max(
        1.35 * inch,
        0.72 * inch + (len(scope_lines) * 0.20 * inch),
    )

    y = check_page(y, scope_height + 1 * inch)

    draw_card(left, y, page_width, scope_height, fill=(1, 1, 1))

    set_fill(gold)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left + 0.22 * inch, y - 0.28 * inch, "SCOPE OF WORK")

    set_fill(black)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(left + 0.22 * inch, y - 0.55 * inch, "Project Overview")

    set_fill(dark_gray)
    pdf.setFont("Helvetica", 10)

    text_y = y - 0.88 * inch

    for line in scope_lines:
        pdf.drawString(left + 0.28 * inch, text_y, f"• {line}")
        text_y -= 0.20 * inch

    y -= scope_height + 0.34 * inch

    # =====================================================
    # PRICE CARD
    # =====================================================

    price_height = 1.45 * inch

    y = check_page(y, price_height + 1 * inch)

    set_fill(black)
    pdf.roundRect(
        left,
        y - price_height,
        page_width,
        price_height,
        14,
        stroke=0,
        fill=1,
    )

    set_fill(gold)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(width / 2, y - 0.36 * inch, "PROJECT TOTAL")

    set_fill((1, 1, 1))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(width / 2, y - 0.88 * inch, money(estimate.total))

    set_fill((0.78, 0.78, 0.78))
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        width / 2,
        y - 1.18 * inch,
        "Includes approved scope, standard labor, and listed project pricing.",
    )

    y -= price_height + 0.36 * inch

    # =====================================================
    # TERMS CARD
    # =====================================================

    terms = estimate.terms or (
        "Estimate valid for 30 days. Pricing is subject to utility requirements, "
        "material availability, permits, and field conditions discovered during work."
    )

    terms_lines = wrap_text(terms, 94)
    terms_height = max(
        1.05 * inch,
        0.60 * inch + (len(terms_lines) * 0.17 * inch),
    )

    y = check_page(y, terms_height + 1 * inch)

    draw_card(left, y, page_width, terms_height, fill=soft_gray)

    set_fill(gold)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left + 0.22 * inch, y - 0.28 * inch, "TERMS")

    set_fill(dark_gray)
    pdf.setFont("Helvetica", 9)

    terms_y = y - 0.58 * inch

    for line in terms_lines:
        pdf.drawString(left + 0.22 * inch, terms_y, line)
        terms_y -= 0.17 * inch

    y -= terms_height + 0.44 * inch

    # =====================================================
    # ACCEPTANCE / SIGNATURE
    # =====================================================

    signature_height = 1.15 * inch

    y = check_page(y, signature_height + 1 * inch)

    set_fill((1, 1, 1))
    set_stroke(light_gray)

    pdf.roundRect(
        left,
        y - signature_height,
        page_width,
        signature_height,
        10,
        stroke=1,
        fill=0,
    )

    set_fill(black)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left + 0.22 * inch, y - 0.30 * inch, "Acceptance")

    set_fill(mid_gray)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        left + 0.22 * inch,
        y - 0.52 * inch,
        "By signing below, customer authorizes JCV Power Solutions to proceed with the approved scope.",
    )

    line_y = y - 0.87 * inch

    set_stroke(black)

    pdf.line(left + 0.22 * inch, line_y, left + 3.30 * inch, line_y)
    pdf.line(right - 2.35 * inch, line_y, right - 0.22 * inch, line_y)

    set_fill(mid_gray)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(left + 0.22 * inch, line_y - 0.16 * inch, "Customer Signature")
    pdf.drawString(right - 2.35 * inch, line_y - 0.16 * inch, "Date")

    draw_footer()

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