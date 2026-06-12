from django.urls import path

from . import views
from . import customer_views
from . import job_views
from . import estimate_views
from . import invoice_views
from . import task_views


urlpatterns = [

    # =====================================================
    # HOME / DASHBOARD
    # =====================================================

    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # =====================================================
    # GLOBAL SEARCH
    # =====================================================

    path("search/", views.global_search, name="global_search"),

    # =====================================================
    # LEADS
    # =====================================================

    path("leads/", customer_views.leads, name="leads"),
    path("leads/<int:lead_id>/", customer_views.lead_detail, name="lead_detail"),
    path("leads/<int:lead_id>/convert/", customer_views.convert_lead, name="convert_lead"),
    path("leads/<int:lead_id>/delete/", customer_views.delete_lead, name="delete_lead"),

    # =====================================================
    # CUSTOMERS
    # =====================================================

    path("customers/", customer_views.customers, name="customers"),
    path("customers/create/", customer_views.create_customer, name="create_customer"),
    path("customers/<int:customer_id>/", customer_views.customer_detail, name="customer_detail"),
    path("customers/<int:customer_id>/edit/", customer_views.edit_customer, name="edit_customer"),
    path("customers/<int:customer_id>/delete/", customer_views.delete_customer, name="delete_customer"),
    path("customers/<int:customer_id>/create-job/", job_views.create_job, name="create_job"),

    # =====================================================
    # JOBS
    # =====================================================

    path("jobs/", job_views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", job_views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/edit/", job_views.edit_job, name="edit_job"),
    path("jobs/<int:job_id>/delete/", job_views.delete_job, name="delete_job"),
    path("jobs/<int:job_id>/update-status/", job_views.update_job_status, name="update_job_status"),
    path("jobs/<int:job_id>/add-note/", job_views.add_job_note, name="add_job_note"),
    path(
    "jobs/<int:job_id>/jarvis/material-review/",
    job_views.run_jarvis_material_review,
    name="run_jarvis_material_review",
),

path(
    "jarvis/reviews/<int:review_id>/apply/",
    job_views.apply_jarvis_review_actions,
    name="apply_jarvis_review_actions",
),

path(
    "jarvis/reviews/<int:review_id>/ignore/",
    job_views.ignore_jarvis_review,
    name="ignore_jarvis_review",
),

path(
    "jobs/<int:job_id>/create-estimate/",
    estimate_views.create_estimate_from_job,
    name="create_estimate_from_job",
),
    path("jobs/<int:job_id>/create-invoice/", invoice_views.create_invoice_from_job, name="create_invoice_from_job"),

    # =====================================================
    # JOB MATERIALS
    # =====================================================

    path("jobs/<int:job_id>/materials/", job_views.job_material_list, name="job_material_list"),
    path("jobs/<int:job_id>/materials/add/", job_views.add_catalog_material_to_job, name="add_catalog_material_to_job"),
    path("jobs/<int:job_id>/materials/auto-populate/", job_views.auto_populate_job_materials, name="auto_populate_job_materials"),
    path("jobs/materials/<int:material_id>/increase/", job_views.increase_job_material, name="increase_job_material"),
    path("jobs/materials/<int:material_id>/decrease/", job_views.decrease_job_material, name="decrease_job_material"),
    path("jobs/materials/<int:material_id>/delete/", job_views.delete_job_material, name="delete_job_material"),
    path("jobs/materials/<int:material_id>/update-quantity/", job_views.update_job_material_quantity, name="update_job_material_quantity"),

    # =====================================================
    # ESTIMATES
    # IMPORTANT: public route must come before estimates/<int:estimate_id>/
    # =====================================================

    path("estimates/", estimate_views.estimates, name="estimates"),

    path(
        "estimates/public/<str:token>/",
        estimate_views.public_estimate_detail,
        name="public_estimate_detail",
    ),

    path("estimates/<int:estimate_id>/", estimate_views.estimate_detail, name="estimate_detail"),
    path("estimates/<int:estimate_id>/edit/", estimate_views.edit_estimate, name="edit_estimate"),
    path("estimates/<int:estimate_id>/approve/", estimate_views.approve_estimate, name="approve_estimate"),
    path("estimates/<int:estimate_id>/delete/", estimate_views.delete_estimate, name="delete_estimate"),
    path("estimates/<int:estimate_id>/pdf/", estimate_views.estimate_pdf, name="estimate_pdf"),

    # =====================================================
    # INVOICES
    # =====================================================

    path("invoices/", invoice_views.invoices, name="invoices"),
    path("invoices/<int:invoice_id>/", invoice_views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:invoice_id>/edit/", invoice_views.edit_invoice, name="edit_invoice"),
    path("invoices/<int:invoice_id>/add-payment/", invoice_views.add_payment, name="add_payment"),

    # =====================================================
    # TASKS
    # =====================================================

    path("tasks/", task_views.tasks, name="tasks"),
    path("tasks/create/", task_views.create_task, name="create_task"),
    path("tasks/<int:task_id>/complete/", task_views.complete_task, name="complete_task"),

]