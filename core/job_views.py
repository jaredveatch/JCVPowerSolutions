from decimal import Decimal

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .models import (
    Customer,
    ServiceTemplate,
    ServiceTemplateMaterial,
    MaterialCatalog,
    Job,
    JobMaterial,
    Estimate,
    Invoice,
    JobNote,
    JarvisJobReview,
)

from core.services.jarvis.dashboard_advisor import create_dashboard_jarvis_review


def get_material_markup_percent(material):
    unit_cost = Decimal(str(material.unit_cost or 0))
    sell_price = Decimal(str(material.sell_price or 0))

    if unit_cost > 0 and sell_price > 0:
        return ((sell_price / unit_cost) - Decimal("1.00")) * Decimal("100.00")

    return Decimal(str(material.material_markup or 0))


def create_or_update_job_material_from_template(job, template_material):
    material = template_material.material
    quantity = Decimal(str(template_material.quantity or 1))
    material_markup = get_material_markup_percent(material)

    existing_material = JobMaterial.objects.filter(
        job=job,
        material=material,
    ).first()

    if existing_material:
        existing_material.quantity = quantity
        existing_material.unit_cost = material.unit_cost or Decimal("0.00")
        existing_material.labor_hours = Decimal("0.00")
        existing_material.material_markup = material_markup
        existing_material.save()
        return existing_material, False

    item = JobMaterial.objects.create(
        job=job,
        material=material,
        quantity=quantity,
        unit_cost=material.unit_cost or Decimal("0.00"),
        labor_hours=Decimal("0.00"),
        material_markup=material_markup,
    )

    return item, True


def create_or_update_job_material(job, material, quantity):
    quantity = Decimal(str(quantity or 1))
    material_markup = get_material_markup_percent(material)

    existing = JobMaterial.objects.filter(
        job=job,
        material=material,
    ).first()

    if existing:
        existing.quantity = quantity
        existing.unit_cost = material.unit_cost or Decimal("0.00")
        existing.labor_hours = Decimal("0.00")
        existing.material_markup = material_markup
        existing.save()
        return existing, False

    item = JobMaterial.objects.create(
        job=job,
        material=material,
        quantity=quantity,
        unit_cost=material.unit_cost or Decimal("0.00"),
        labor_hours=Decimal("0.00"),
        material_markup=material_markup,
    )

    return item, True


@staff_member_required
def create_job(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    template_groups = []

    template_categories = (
        ServiceTemplate.objects
        .filter(active=True)
        .exclude(category__isnull=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    for category in template_categories:
        templates = (
            ServiceTemplate.objects
            .filter(active=True, category=category)
            .order_by("name")
        )

        template_groups.append({
            "category": category,
            "templates": templates,
        })

    uncategorized_templates = (
        ServiceTemplate.objects
        .filter(active=True)
        .filter(Q(category__isnull=True) | Q(category=""))
        .order_by("name")
    )

    if uncategorized_templates.exists():
        template_groups.append({
            "category": "Uncategorized",
            "templates": uncategorized_templates,
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
            template_materials = (
                ServiceTemplateMaterial.objects
                .filter(service_template=template)
                .select_related("material")
            )

            for template_material in template_materials:
                create_or_update_job_material_from_template(job, template_material)

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

    latest_jarvis_review = (
        job.jarvis_reviews
        .all()
        .order_by("-created_at")
        .first()
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
        "sell_total": job.sell_total(),
        "latest_jarvis_review": latest_jarvis_review,
    })


@staff_member_required
def run_jarvis_material_review(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method != "POST":
        return redirect("job_detail", job_id=job.id)

    prompt = request.POST.get("jarvis_prompt", "").strip()

    if not prompt:
        prompt = (
            "Review this job, current materials, template, description, site notes, "
            "and material notes. Recommend add/remove/update material actions."
        )

    review = create_dashboard_jarvis_review(job=job, prompt=prompt)

    messages.success(
        request,
        f"JARVIS reviewed this job and created {len(review.recommendations.get('actions', []))} recommendation(s)."
    )

    return redirect("job_detail", job_id=job.id)


@staff_member_required
def apply_jarvis_review_actions(request, review_id):
    review = get_object_or_404(JarvisJobReview, id=review_id)
    job = review.job

    if request.method != "POST":
        return redirect("job_detail", job_id=job.id)

    selected_indexes = request.POST.getlist("selected_actions")

    if not selected_indexes:
        messages.warning(request, "No JARVIS recommendations were selected.")
        return redirect("job_detail", job_id=job.id)

    actions = review.recommendations.get("actions", [])

    added = 0
    removed = 0
    updated = 0
    skipped = 0

    applied_actions = []

    for index_raw in selected_indexes:
        try:
            index = int(index_raw)
        except ValueError:
            skipped += 1
            continue

        if index < 0 or index >= len(actions):
            skipped += 1
            continue

        action = actions[index]
        action_type = action.get("action")

        if action_type == "add_material":
            material_name = action.get("material_name")
            quantity = Decimal(str(action.get("quantity") or 1))

            material = MaterialCatalog.objects.filter(
                name=material_name,
                active=True,
            ).first()

            if not material:
                skipped += 1
                continue

            create_or_update_job_material(
                job=job,
                material=material,
                quantity=quantity,
            )

            added += 1
            applied_actions.append(action)

        elif action_type == "remove_material":
            job_material_id = action.get("job_material_id")

            item = JobMaterial.objects.filter(
                id=job_material_id,
                job=job,
            ).first()

            if not item:
                skipped += 1
                continue

            item.delete()
            removed += 1
            applied_actions.append(action)

        elif action_type == "update_quantity":
            job_material_id = action.get("job_material_id")
            suggested_quantity = Decimal(str(action.get("suggested_quantity") or 1))

            item = JobMaterial.objects.filter(
                id=job_material_id,
                job=job,
            ).first()

            if not item:
                skipped += 1
                continue

            item.quantity = suggested_quantity
            item.save()

            updated += 1
            applied_actions.append(action)

        else:
            skipped += 1

    review.status = "applied" if len(applied_actions) == len(selected_indexes) else "partially_applied"
    review.applied_at = timezone.now()

    review.recommendations["applied_actions"] = applied_actions
    review.save()

    JobNote.objects.create(
        job=job,
        author=request.user.username,
        note=(
            "JARVIS applied selected recommendations.\n\n"
            f"Added: {added}\n"
            f"Removed: {removed}\n"
            f"Updated: {updated}\n"
            f"Skipped: {skipped}"
        ),
    )

    messages.success(
        request,
        f"JARVIS applied {added} add, {removed} remove, and {updated} update action(s)."
    )

    return redirect("job_detail", job_id=job.id)


@staff_member_required
def ignore_jarvis_review(request, review_id):
    review = get_object_or_404(JarvisJobReview, id=review_id)
    job = review.job

    if request.method == "POST":
        review.status = "ignored"
        review.save()
        messages.info(request, "JARVIS review ignored.")

    return redirect("job_detail", job_id=job.id)


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

    return render(request, "edit_job.html", {
        "job": job,
    })


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
                quantity = Decimal(str(float(quantity_raw)))
                if quantity <= 0:
                    quantity = Decimal("1")
            except ValueError:
                quantity = Decimal("1")

            existing = JobMaterial.objects.filter(
                job=job,
                material=material,
            ).first()

            material_markup = get_material_markup_percent(material)

            if existing:
                existing.quantity = Decimal(str(existing.quantity or 0)) + quantity
                existing.unit_cost = material.unit_cost or Decimal("0.00")
                existing.labor_hours = Decimal("0.00")
                existing.material_markup = material_markup
                existing.save()
            else:
                JobMaterial.objects.create(
                    job=job,
                    material=material,
                    quantity=quantity,
                    unit_cost=material.unit_cost or Decimal("0.00"),
                    labor_hours=Decimal("0.00"),
                    material_markup=material_markup,
                )

        return redirect("job_detail", job_id=job.id)

    return render(request, "add_catalog_material_to_job.html", {
        "job": job,
        "catalog_materials": catalog_materials,
    })


@staff_member_required
def auto_populate_job_materials(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method != "POST":
        return redirect("job_detail", job_id=job.id)

    if not job.template:
        messages.error(request, "This job does not have a service template selected.")
        return redirect("job_detail", job_id=job.id)

    template_materials = (
        ServiceTemplateMaterial.objects
        .filter(service_template=job.template)
        .select_related("material")
    )

    created = 0
    updated = 0

    for template_material in template_materials:
        _, was_created = create_or_update_job_material_from_template(job, template_material)

        if was_created:
            created += 1
        else:
            updated += 1

    messages.success(
        request,
        f"Imported {created} new materials and updated {updated} existing materials from {job.template.name}."
    )

    return redirect("job_detail", job_id=job.id)


@staff_member_required
def increase_job_material(request, material_id):
    if request.method != "POST":
        return redirect("/jobs/")

    item = get_object_or_404(JobMaterial, id=material_id)
    item.quantity = Decimal(str(item.quantity or 0)) + Decimal("1")
    item.save()

    return redirect("job_detail", job_id=item.job.id)


@staff_member_required
def decrease_job_material(request, material_id):
    if request.method != "POST":
        return redirect("/jobs/")

    item = get_object_or_404(JobMaterial, id=material_id)
    job_id = item.job.id

    if Decimal(str(item.quantity or 0)) > Decimal("1"):
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
        current_quantity = Decimal(str(item.quantity or 1))
    except Exception:
        current_quantity = Decimal("1")

    if action == "plus":
        new_quantity = current_quantity + Decimal("1")
    elif action == "minus":
        new_quantity = current_quantity - Decimal("1")
    elif action == "set":
        try:
            new_quantity = Decimal(str(float(quantity_raw)))
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
            "job_sell_total": f"${job.sell_total():,.2f}",
        })

    item.quantity = new_quantity
    item.save()

    return JsonResponse({
        "success": True,
        "deleted": False,
        "material_id": item.id,
        "quantity": str(item.quantity),
        "material_total": f"${item.material_total:,.2f}",
        "labor_total": f"${item.labor_total:,.2f}",
        "installed_total": f"${item.total_cost:,.2f}",
        "sell_total": f"${item.sell_total:,.2f}",
        "job_material_total": f"${job.material_total():,.2f}",
        "job_labor_total": f"${job.labor_total():,.2f}",
        "job_installed_total": f"${job.installed_total():,.2f}",
        "job_sell_total": f"${job.sell_total():,.2f}",
    })