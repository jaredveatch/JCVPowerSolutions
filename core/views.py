from decimal import Decimal
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    ServiceTemplate,
    ServiceTemplateMaterial,
    MaterialCatalog,
    Job,
    JobMaterial,
    Estimate,
    EstimateLineItem,
    Invoice,
    Payment,
    JobNote,
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
            return JsonResponse({"success": True, "message": "Thank you for submitting your request."})

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
            return JsonResponse({"success": True, "message": "Application submitted successfully."})

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


@staff_member_required
def leads(request):
    return render(request, "leads.html", {
        "leads": QuoteRequest.objects.order_by("-created_at"),
    })


@staff_member_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(QuoteRequest, id=lead_id)
    return render(request, "lead_detail.html", {"lead": lead})


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

    return render(request, "edit_customer.html", {"customer": customer})


@staff_member_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.delete()
        return redirect("/customers/")

    return redirect(f"/customers/{customer.id}/")


# =====================================================
# JOBS
# =====================================================

@staff_member_required
def create_job(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    categories = [
        "Panel / Service Work",
        "Subpanels",
        "Dedicated Circuits",
        "Outlets / Switches",
        "Lighting",
        "Fans",
        "Troubleshooting",
        "Low Voltage",
    ]

    template_groups = []

    for category in categories:
        templates = ServiceTemplate.objects.filter(
            active=True,
            category=category,
        ).order_by("name")

        if templates.exists():
            template_groups.append({
                "category": category,
                "templates": templates,
            })

    other_templates = ServiceTemplate.objects.filter(
        active=True,
    ).exclude(
        category__in=categories,
    ).order_by("category", "name")

    if other_templates.exists():
        template_groups.append({
            "category": "Other",
            "templates": other_templates,
        })

    if request.method == "POST":
        template_id = request.POST.get("template")
        template = ServiceTemplate.objects.filter(id=template_id).first() if template_id else None

        title = request.POST.get("title", "").strip()
        status = request.POST.get("status") or "new"
        priority = request.POST.get("priority") or "normal"
        assigned_to = request.POST.get("assigned_to", "").strip()
        job_address = request.POST.get("job_address", "").strip()
        description = request.POST.get("description", "").strip()
        site_notes = request.POST.get("site_notes", "").strip()
        material_notes = request.POST.get("material_notes", "").strip()

        scheduled_date_raw = request.POST.get("scheduled_date", "").strip()
        scheduled_date = parse_datetime(scheduled_date_raw) if scheduled_date_raw else None

        price_raw = request.POST.get("estimated_total_price", "").strip()

        if price_raw:
            estimated_total_price = Decimal(price_raw)
        elif template:
            estimated_total_price = template.default_price or Decimal("0.00")
        else:
            estimated_total_price = Decimal("0.00")

        if not title and template:
            title = template.name

        if not description and template:
            description = template.customer_description or ""

        if not material_notes and template:
            material_notes = template.internal_checklist or ""

        job = Job.objects.create(
            customer=customer,
            template=template,
            title=title or "New Job",
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            job_address=job_address,
            description=description,
            site_notes=site_notes,
            material_notes=material_notes,
            estimated_total_price=estimated_total_price,
            scheduled_date=scheduled_date,
        )

        if template:
            template_materials = ServiceTemplateMaterial.objects.filter(
                service_template=template,
            ).select_related("material")

            for template_material in template_materials:
                material = template_material.material

                existing_material = JobMaterial.objects.filter(
                    job=job,
                    material=material,
                ).first()

                if existing_material:
                    existing_material.quantity = Decimal("1")
                    existing_material.unit_cost = material.unit_cost or Decimal("0.00")
                    existing_material.labor_hours = material.labor_hours or Decimal("0.00")
                    existing_material.save()
                else:
                    JobMaterial.objects.create(
                        job=job,
                        material=material,
                        quantity=Decimal("1"),
                        unit_cost=material.unit_cost or Decimal("0.00"),
                        labor_hours=material.labor_hours or Decimal("0.00"),
                    )

        return redirect("job_detail", job_id=job.id)

    return render(request, "create_job.html", {
        "customer": customer,
        "template_groups": template_groups,
    })


@staff_member_required
def jobs(request):
    return render(request, "jobs.html", {
        "jobs": Job.objects.all().order_by("-created_at"),
    })


@staff_member_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    job_materials = job.job_materials.all().order_by(
        "-total_cost",
        "-labor_total",
        "-material_total",
        "material__name",
    )

    return render(request, "job_detail.html", {
        "job": job,
        "estimates": Estimate.objects.filter(job=job).order_by("-created_at"),
        "invoices": Invoice.objects.filter(job=job).order_by("-created_at"),
        "notes": job.notes.all().order_by("-created_at"),
        "tasks": job.tasks.all().order_by("-created_at"),
        "job_materials": job_materials,
        "catalog_materials": MaterialCatalog.objects.filter(active=True).order_by("name"),
        "material_total": job.material_total(),
        "labor_total": job.labor_total(),
        "installed_total": job.installed_total(),
    })


@staff_member_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        job.title = request.POST.get("title") or "New Job"
        job.status = request.POST.get("status") or "new"
        job.priority = request.POST.get("priority") or "normal"
        job.assigned_to = request.POST.get("assigned_to")
        job.job_address = request.POST.get("job_address")
        job.description = request.POST.get("description")
        job.site_notes = request.POST.get("site_notes")
        job.material_notes = request.POST.get("material_notes")

        price = request.POST.get("estimated_total_price", "").strip()
        job.estimated_total_price = Decimal(price) if price else Decimal("0.00")

        job.save()

        return redirect(f"/jobs/{job.id}/")

    return render(request, "edit_job.html", {"job": job})


@staff_member_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    customer_id = job.customer.id

    if request.method == "POST":
        job.delete()
        return redirect(f"/customers/{customer_id}/")

    return redirect(f"/jobs/{job.id}/")


@staff_member_required
def update_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        status = request.POST.get("status")

        if status:
            job.status = status

        if status == "completed":
            job.completed_at = timezone.now()

        job.save()

    return redirect(f"/jobs/{job.id}/")


@staff_member_required
def add_job_note(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        note = request.POST.get("note")

        if note:
            JobNote.objects.create(
                job=job,
                author=request.user.username,
                note=note,
            )

    return redirect(f"/jobs/{job.id}/")


# =====================================================
# JOB MATERIALS
# =====================================================

@staff_member_required
def job_material_list(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(request, "job_material_list.html", {
        "job": job,
        "job_materials": job.job_materials.all().order_by(
            "-total_cost",
            "-labor_total",
            "-material_total",
            "material__name",
        ),
    })


@staff_member_required
def add_catalog_material_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    catalog_materials = MaterialCatalog.objects.filter(active=True).order_by("name")

    if request.method == "POST":
        material_id = request.POST.get("material")
        quantity_raw = request.POST.get("quantity") or "1"

        if material_id:
            material = get_object_or_404(MaterialCatalog, id=material_id)

            try:
                quantity = max(int(float(quantity_raw)), 1)
            except ValueError:
                quantity = 1

            existing = JobMaterial.objects.filter(
                job=job,
                material=material,
            ).first()

            if existing:
                existing.quantity = Decimal(str(existing.quantity)) + Decimal(str(quantity))
                existing.unit_cost = material.unit_cost or Decimal("0.00")
                existing.labor_hours = material.labor_hours or Decimal("0.00")
                existing.save()
            else:
                JobMaterial.objects.create(
                    job=job,
                    material=material,
                    quantity=Decimal(str(quantity)),
                    unit_cost=material.unit_cost or Decimal("0.00"),
                    labor_hours=material.labor_hours or Decimal("0.00"),
                )

        return redirect("job_detail", job_id=job.id)

    return render(request, "add_catalog_material_to_job.html", {
        "job": job,
        "catalog_materials": catalog_materials,
    })


@staff_member_required
def increase_job_material(request, material_id):
    if request.method != "POST":
        return redirect("/jobs/")

    item = get_object_or_404(JobMaterial, id=material_id)

    item.quantity = Decimal(str(item.quantity)) + Decimal("1")
    item.save()

    return redirect("job_detail", job_id=item.job.id)


@staff_member_required
def decrease_job_material(request, material_id):
    if request.method != "POST":
        return redirect("/jobs/")

    item = get_object_or_404(JobMaterial, id=material_id)
    job_id = item.job.id

    if Decimal(str(item.quantity)) > Decimal("1"):
        item.quantity = Decimal(str(item.quantity)) - Decimal("1")
        item.save()
    else:
        item.delete()

    return redirect("job_detail", job_id=job_id)


@staff_member_required
def delete_job_material(request, material_id):
    if request.method != "POST":
        return redirect("/jobs/")

    item = get_object_or_404(JobMaterial, id=material_id)
    job_id = item.job.id

    item.delete()

    return redirect("job_detail", job_id=job_id)


@staff_member_required
def update_job_material_quantity(request, material_id):
    item = get_object_or_404(JobMaterial, id=material_id)
    job = item.job

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "POST required",
        }, status=400)

    action = request.POST.get("action")
    quantity_raw = request.POST.get("quantity", "0")

    try:
        current_quantity = int(item.quantity)
    except ValueError:
        current_quantity = 1

    if action == "plus":
        new_quantity = current_quantity + 1

    elif action == "minus":
        new_quantity = current_quantity - 1

    elif action == "set":
        try:
            new_quantity = int(float(quantity_raw))
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": "Invalid quantity",
            }, status=400)

    else:
        return JsonResponse({
            "success": False,
            "error": "Invalid action",
        }, status=400)

    if new_quantity <= 0:
        item_id = item.id
        item.delete()

        return JsonResponse({
            "success": True,
            "deleted": True,
            "material_id": item_id,
            "job_material_total": f"${job.material_total():,.2f}",
            "job_labor_total": f"${job.labor_total():,.2f}",
            "job_installed_total": f"${job.installed_total():,.2f}",
        })

    item.quantity = Decimal(str(new_quantity))
    item.save()

    return JsonResponse({
        "success": True,
        "deleted": False,
        "material_id": item.id,
        "quantity": int(item.quantity),
        "material_total": f"${item.material_total:,.2f}",
        "labor_total": f"${item.labor_total:,.2f}",
        "installed_total": f"${item.total_cost:,.2f}",
        "job_material_total": f"${job.material_total():,.2f}",
        "job_labor_total": f"${job.labor_total():,.2f}",
        "job_installed_total": f"${job.installed_total():,.2f}",
    })


# =====================================================
# ESTIMATES
# =====================================================

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
    y = height - 0.85 * inch

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(0.75 * inch, y, "JCV Power Solutions")

    y -= 0.28 * inch
    pdf.setFont("Helvetica", 11)
    pdf.drawString(0.75 * inch, y, "Professional Electrical Services")

    y -= 0.60 * inch
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(0.75 * inch, y, "Customer Estimate")

    y -= 0.45 * inch

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(0.75 * inch, y, "Customer:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(1.75 * inch, y, estimate.job.customer.name)

    y -= 0.24 * inch

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(0.75 * inch, y, "Project:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(1.75 * inch, y, estimate.job.title[:75])

    y -= 0.24 * inch

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(0.75 * inch, y, "Date:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(1.75 * inch, y, estimate.created_at.strftime("%m/%d/%Y"))

    y -= 0.50 * inch

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(0.75 * inch, y, "Scope of Work")

    y -= 0.30 * inch
    pdf.setFont("Helvetica", 11)

    scope = estimate.scope_of_work or "Electrical work as discussed."

    for line in scope.splitlines():
        if y < 1.60 * inch:
            pdf.showPage()
            y = height - 0.85 * inch
            pdf.setFont("Helvetica", 11)

        pdf.drawString(0.90 * inch, y, line[:95])
        y -= 0.22 * inch

    y -= 0.30 * inch

    if estimate.exclusions:
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawString(0.75 * inch, y, "Exclusions")

        y -= 0.30 * inch
        pdf.setFont("Helvetica", 10)

        for line in estimate.exclusions.splitlines():
            if y < 1.60 * inch:
                pdf.showPage()
                y = height - 0.85 * inch
                pdf.setFont("Helvetica", 10)

            pdf.drawString(0.90 * inch, y, line[:100])
            y -= 0.20 * inch

        y -= 0.30 * inch

    if y < 3 * inch:
        pdf.showPage()
        y = height - 0.85 * inch

    pdf.roundRect(
        4.5 * inch,
        y - 0.55 * inch,
        2.25 * inch,
        0.75 * inch,
        8,
        stroke=1,
        fill=0,
    )

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(4.75 * inch, y - 0.15 * inch, "Project Total")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(4.75 * inch, y - 0.45 * inch, f"${estimate.total:,.2f}")

    y -= 1.10 * inch

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(0.75 * inch, y, "Terms & Conditions")

    y -= 0.30 * inch
    pdf.setFont("Helvetica", 9)

    terms = estimate.terms or (
        "Estimate valid for 30 days. Material pricing subject to availability "
        "and utility requirements."
    )

    for line in terms.splitlines():
        if y < 1.80 * inch:
            pdf.showPage()
            y = height - 0.85 * inch
            pdf.setFont("Helvetica", 9)

        pdf.drawString(0.90 * inch, y, line[:110])
        y -= 0.18 * inch

    y -= 0.60 * inch

    if y < 1.50 * inch:
        pdf.showPage()
        y = height - 0.85 * inch

    pdf.line(0.75 * inch, y, 3.50 * inch, y)
    pdf.drawString(0.75 * inch, y - 0.18 * inch, "Customer Signature")

    pdf.line(4.50 * inch, y, 7.25 * inch, y)
    pdf.drawString(4.50 * inch, y - 0.18 * inch, "Date")

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


# =====================================================
# INVOICES
# =====================================================

@staff_member_required
def invoices(request):
    return render(request, "invoices.html", {
        "invoices": Invoice.objects.all().order_by("-created_at"),
    })


@staff_member_required
def create_invoice_from_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    subtotal = job.installed_total() or job.estimated_total_price or Decimal("0.00")

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
        invoice.save()

        return redirect(f"/invoices/{invoice.id}/")

    return render(request, "edit_invoice.html", {"invoice": invoice})


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


# =====================================================
# TASKS
# =====================================================

@staff_member_required
def tasks(request):
    return render(request, "tasks.html", {
        "tasks": Task.objects.all().order_by("status", "due_date"),
    })


@staff_member_required
def create_task(request):
    customers_list = Customer.objects.all()
    jobs_list = Job.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        job_id = request.POST.get("job")

        customer = Customer.objects.filter(id=customer_id).first() if customer_id else None
        job = Job.objects.filter(id=job_id).first() if job_id else None

        Task.objects.create(
            title=request.POST.get("title"),
            customer=customer,
            job=job,
            assigned_to=request.POST.get("assigned_to"),
            priority=request.POST.get("priority", "normal"),
            notes=request.POST.get("notes", ""),
        )

        return redirect("/tasks/")

    return render(request, "create_task.html", {
        "customers": customers_list,
        "jobs": jobs_list,
    })


@staff_member_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = "completed"
    task.save()

    return redirect("/tasks/")