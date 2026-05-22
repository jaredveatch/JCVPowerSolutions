from decimal import Decimal

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)

from django.http import JsonResponse

from django.contrib.admin.views.decorators import (
    staff_member_required
)

from django.db.models import Q

from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    ServiceTemplate,
    Job,
    Estimate,
    Invoice,
    Payment,
    JobNote,
    Task,
)


# =========================================================
# HOME PAGE
# =========================================================

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
                "message": "Thank you for submitting your request."
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
                "message": "Application submitted successfully."
            })

    return render(request, "home.html")


# =========================================================
# DASHBOARD
# =========================================================

@staff_member_required
def dashboard(request):

    context = {

        "new_quotes":
            QuoteRequest.objects.order_by("-created_at")[:5],

        "recent_jobs":
            Job.objects.order_by("-created_at")[:5],

        "recent_tasks":
            Task.objects.filter(
                status="open"
            ).order_by("due_date")[:5],

        "quotes_count":
            QuoteRequest.objects.count(),

        "customers_count":
            Customer.objects.count(),

        "jobs_count":
            Job.objects.count(),

        "estimates_count":
            Estimate.objects.count(),

        "invoices_count":
            Invoice.objects.count(),

        "open_tasks_count":
            Task.objects.filter(
                status="open"
            ).count(),
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =========================================================
# GLOBAL SEARCH
# =========================================================

@staff_member_required
def global_search(request):

    query = request.GET.get("q", "").strip()

    customers = []
    jobs = []
    invoices = []

    if query:

        customers = Customer.objects.filter(
            Q(name__icontains=query)
            |
            Q(phone__icontains=query)
            |
            Q(email__icontains=query)
        )

        jobs = Job.objects.filter(
            Q(title__icontains=query)
            |
            Q(job_address__icontains=query)
            |
            Q(description__icontains=query)
        )

        invoices = Invoice.objects.filter(
            Q(invoice_number__icontains=query)
            |
            Q(title__icontains=query)
        )

    return render(
        request,
        "search_results.html",
        {
            "query": query,
            "customers": customers,
            "jobs": jobs,
            "invoices": invoices,
        }
    )


# =========================================================
# LEADS
# =========================================================

@staff_member_required
def leads(request):

    return render(
        request,
        "leads.html",
        {
            "leads":
                QuoteRequest.objects.order_by("-created_at")
        }
    )


@staff_member_required
def lead_detail(request, lead_id):

    lead = get_object_or_404(
        QuoteRequest,
        id=lead_id
    )

    return render(
        request,
        "lead_detail.html",
        {
            "lead": lead
        }
    )


@staff_member_required
def convert_lead(request, lead_id):

    lead = get_object_or_404(
        QuoteRequest,
        id=lead_id
    )

    customer = Customer.objects.create(
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        notes=lead.message,
        status="active",
    )

    lead.status = "converted"
    lead.save()

    return redirect(
        f"/customers/{customer.id}/"
    )


@staff_member_required
def delete_lead(request, lead_id):

    lead = get_object_or_404(
        QuoteRequest,
        id=lead_id
    )

    if request.method == "POST":

        lead.delete()

        return redirect("/leads/")

    return redirect(
        f"/leads/{lead.id}/"
    )


# =========================================================
# CUSTOMERS
# =========================================================

@staff_member_required
def customers(request):

    customers = Customer.objects.all().order_by("-id")

    return render(
        request,
        "customers.html",
        {
            "customers": customers
        }
    )


@staff_member_required
def create_customer(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        if name and phone:

            existing_customer = Customer.objects.filter(
                phone=phone
            ).first()

            if existing_customer:

                return redirect(
                    f"/customers/{existing_customer.id}/"
                )

            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                status="active",
            )

            return redirect(
                f"/customers/{customer.id}/"
            )

    return redirect("/customers/")


@staff_member_required
def customer_detail(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    jobs = customer.jobs.all().order_by(
        "-created_at"
    )

    tasks = customer.tasks.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "customer_detail.html",
        {
            "customer": customer,
            "jobs": jobs,
            "tasks": tasks,
        }
    )


@staff_member_required
def edit_customer(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

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

        return redirect(
            f"/customers/{customer.id}/"
        )

    return render(
        request,
        "edit_customer.html",
        {
            "customer": customer
        }
    )


@staff_member_required
def delete_customer(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == "POST":

        customer.delete()

        return redirect("/customers/")

    return redirect(
        f"/customers/{customer.id}/"
    )


# =========================================================
# JOBS
# =========================================================

@staff_member_required
def create_job(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    templates = ServiceTemplate.objects.filter(
        active=True
    ).order_by(
        "category",
        "name"
    )

    if request.method == "POST":

        template_id = request.POST.get("template")

        template = None

        if template_id:

            template = ServiceTemplate.objects.filter(
                id=template_id
            ).first()

        title = request.POST.get(
            "title",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "site_visit"
        )

        priority = request.POST.get(
            "priority",
            "normal"
        )

        assigned_to = request.POST.get(
            "assigned_to",
            ""
        )

        job_address = request.POST.get(
            "job_address",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        site_notes = request.POST.get(
            "site_notes",
            ""
        ).strip()

        material_notes = request.POST.get(
            "material_notes",
            ""
        ).strip()

        scheduled_date_raw = request.POST.get(
            "scheduled_date",
            ""
        ).strip()

        scheduled_date = None

        if scheduled_date_raw:

            scheduled_date = parse_datetime(
                scheduled_date_raw
            )

        estimated_total_price = None

        price_raw = request.POST.get(
            "estimated_total_price",
            ""
        ).strip()

        if price_raw:

            estimated_total_price = Decimal(
                price_raw
            )

        elif template:

            estimated_total_price = (
                template.default_price
            )

        if not title and template:

            title = template.name

        if not description and template:

            description = (
                template.customer_description
            )

        if not material_notes and template:

            material_notes = (
                template.internal_checklist
            )

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

        return redirect(
            f"/jobs/{job.id}/"
        )

    return render(
        request,
        "create_job.html",
        {
            "customer": customer,
            "templates": templates,
        }
    )


@staff_member_required
def jobs(request):

    jobs = Job.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "jobs.html",
        {
            "jobs": jobs
        }
    )


@staff_member_required
def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    estimates = Estimate.objects.filter(
        job=job
    ).order_by("-created_at")

    invoices = Invoice.objects.filter(
        job=job
    ).order_by("-created_at")

    notes = job.notes.all().order_by(
        "-created_at"
    )

    tasks = job.tasks.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "job_detail.html",
        {
            "job": job,
            "estimates": estimates,
            "invoices": invoices,
            "notes": notes,
            "tasks": tasks,
        }
    )


@staff_member_required
def edit_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if request.method == "POST":

        job.title = request.POST.get("title")
        job.status = request.POST.get("status")
        job.priority = request.POST.get("priority")
        job.assigned_to = request.POST.get("assigned_to")
        job.job_address = request.POST.get("job_address")
        job.description = request.POST.get("description")
        job.site_notes = request.POST.get("site_notes")
        job.material_notes = request.POST.get("material_notes")

        price = request.POST.get(
            "estimated_total_price",
            "0"
        )

        job.estimated_total_price = Decimal(price)

        job.save()

        return redirect(
            f"/jobs/{job.id}/"
        )

    return render(
        request,
        "edit_job.html",
        {
            "job": job
        }
    )


@staff_member_required
def delete_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    customer_id = job.customer.id

    if request.method == "POST":

        job.delete()

        return redirect(
            f"/customers/{customer_id}/"
        )

    return redirect(
        f"/jobs/{job.id}/"
    )


@staff_member_required
def update_job_status(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if request.method == "POST":

        status = request.POST.get("status")

        if status:
            job.status = status

        if status == "completed":
            job.completed_at = timezone.now()

        job.save()

    return redirect(
        f"/jobs/{job.id}/"
    )


@staff_member_required
def add_job_note(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if request.method == "POST":

        note = request.POST.get("note")

        if note:

            JobNote.objects.create(
                job=job,
                author=request.user.username,
                note=note,
            )

    return redirect(
        f"/jobs/{job.id}/"
    )


# =========================================================
# ESTIMATES
# =========================================================

@staff_member_required
def estimates(request):

    estimates = Estimate.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "estimates.html",
        {
            "estimates": estimates
        }
    )


@staff_member_required
def create_estimate_from_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    scope = (
        job.description
        or
        "Electrical work as discussed during walkthrough."
    )

    subtotal = (
        job.estimated_total_price
        or
        Decimal("0.00")
    )

    estimate = Estimate.objects.create(
        job=job,
        title=f"Estimate - {job.title}",
        scope_of_work=scope,
        subtotal=subtotal,
        tax=Decimal("0.00"),
        total=subtotal,
        status="draft",
    )

    job.status = "estimate_sent"
    job.save()

    return redirect(
        f"/estimates/{estimate.id}/"
    )


@staff_member_required
def estimate_detail(request, estimate_id):

    estimate = get_object_or_404(
        Estimate,
        id=estimate_id
    )

    return render(
        request,
        "estimate_detail.html",
        {
            "estimate": estimate
        }
    )


@staff_member_required
def edit_estimate(request, estimate_id):

    estimate = get_object_or_404(
        Estimate,
        id=estimate_id
    )

    if request.method == "POST":

        estimate.title = request.POST.get("title")
        estimate.scope_of_work = request.POST.get("scope_of_work")
        estimate.exclusions = request.POST.get("exclusions")
        estimate.terms = request.POST.get("terms")

        subtotal = request.POST.get(
            "subtotal",
            "0"
        )

        tax = request.POST.get(
            "tax",
            "0"
        )

        estimate.subtotal = Decimal(subtotal)
        estimate.tax = Decimal(tax)

        estimate.save()

        return redirect(
            f"/estimates/{estimate.id}/"
        )

    return render(
        request,
        "edit_estimate.html",
        {
            "estimate": estimate
        }
    )


@staff_member_required
def approve_estimate(request, estimate_id):

    estimate = get_object_or_404(
        Estimate,
        id=estimate_id
    )

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
        }
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

    return redirect(
        f"/invoices/{invoice.id}/"
    )


@staff_member_required
def delete_estimate(request, estimate_id):

    estimate = get_object_or_404(
        Estimate,
        id=estimate_id
    )

    job_id = estimate.job.id

    if request.method == "POST":

        estimate.delete()

        return redirect(
            f"/jobs/{job_id}/"
        )

    return redirect(
        f"/estimates/{estimate.id}/"
    )


# =========================================================
# INVOICES
# =========================================================

@staff_member_required
def invoices(request):

    invoices = Invoice.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "invoices.html",
        {
            "invoices": invoices
        }
    )


@staff_member_required
def create_invoice_from_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    invoice = Invoice.objects.create(
        job=job,
        title=f"Invoice - {job.title}",
        description=job.description,
        subtotal=job.estimated_total_price or Decimal("0.00"),
        tax=Decimal("0.00"),
        total=job.estimated_total_price or Decimal("0.00"),
        due_date=timezone.now().date(),
        status="sent",
    )

    return redirect(
        f"/invoices/{invoice.id}/"
    )


@staff_member_required
def invoice_detail(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    payments = invoice.payments.all().order_by(
        "-paid_at"
    )

    return render(
        request,
        "invoice_detail.html",
        {
            "invoice": invoice,
            "payments": payments,
        }
    )


@staff_member_required
def edit_invoice(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    if request.method == "POST":

        invoice.title = request.POST.get("title")
        invoice.description = request.POST.get("description")
        invoice.status = request.POST.get("status")

        subtotal = request.POST.get(
            "subtotal",
            "0"
        )

        tax = request.POST.get(
            "tax",
            "0"
        )

        invoice.subtotal = Decimal(subtotal)
        invoice.tax = Decimal(tax)

        invoice.save()

        return redirect(
            f"/invoices/{invoice.id}/"
        )

    return render(
        request,
        "edit_invoice.html",
        {
            "invoice": invoice
        }
    )


@staff_member_required
def add_payment(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    if request.method == "POST":

        amount = request.POST.get("amount")

        if amount:

            Payment.objects.create(
                invoice=invoice,
                amount=Decimal(amount),
                method=request.POST.get(
                    "method",
                    "card"
                ),
                reference=request.POST.get(
                    "reference",
                    ""
                ),
                notes=request.POST.get(
                    "notes",
                    ""
                ),
            )

    return redirect(
        f"/invoices/{invoice.id}/"
    )


# =========================================================
# TASKS
# =========================================================

@staff_member_required
def tasks(request):

    tasks = Task.objects.all().order_by(
        "status",
        "due_date"
    )

    return render(
        request,
        "tasks.html",
        {
            "tasks": tasks
        }
    )


@staff_member_required
def create_task(request):

    customers = Customer.objects.all()
    jobs = Job.objects.all()

    if request.method == "POST":

        customer_id = request.POST.get(
            "customer"
        )

        job_id = request.POST.get(
            "job"
        )

        customer = None
        job = None

        if customer_id:
            customer = Customer.objects.filter(
                id=customer_id
            ).first()

        if job_id:
            job = Job.objects.filter(
                id=job_id
            ).first()

        Task.objects.create(
            title=request.POST.get("title"),
            customer=customer,
            job=job,
            assigned_to=request.POST.get(
                "assigned_to"
            ),
            priority=request.POST.get(
                "priority",
                "normal"
            ),
            notes=request.POST.get(
                "notes",
                ""
            ),
        )

        return redirect("/tasks/")

    return render(
        request,
        "create_task.html",
        {
            "customers": customers,
            "jobs": jobs,
        }
    )


@staff_member_required
def complete_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    task.status = "completed"
    task.save()

    return redirect("/tasks/")