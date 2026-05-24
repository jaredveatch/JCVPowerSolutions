from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Customer,
    Job,
    Task,
)


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

        customer = (
            Customer.objects
            .filter(id=customer_id)
            .first()
            if customer_id
            else None
        )

        job = (
            Job.objects
            .filter(id=job_id)
            .first()
            if job_id
            else None
        )

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