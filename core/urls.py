from django.urls import path
from . import views


urlpatterns = [

    # HOME / DASHBOARD
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # GLOBAL SEARCH
    path("search/", views.global_search, name="global_search"),

    # LEADS
    path("leads/", views.leads, name="leads"),
    path("leads/<int:lead_id>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:lead_id>/convert/", views.convert_lead, name="convert_lead"),
    path("leads/<int:lead_id>/delete/", views.delete_lead, name="delete_lead"),

    # CUSTOMERS
    path("customers/", views.customers, name="customers"),
    path("customers/create/", views.create_customer, name="create_customer"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:customer_id>/edit/", views.edit_customer, name="edit_customer"),
    path("customers/<int:customer_id>/delete/", views.delete_customer, name="delete_customer"),
    path("customers/<int:customer_id>/create-job/", views.create_job, name="create_job"),

    # JOBS
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("jobs/<int:job_id>/delete/", views.delete_job, name="delete_job"),
    path("jobs/<int:job_id>/update-status/", views.update_job_status, name="update_job_status"),
    path("jobs/<int:job_id>/add-note/", views.add_job_note, name="add_job_note"),
    path("jobs/<int:job_id>/create-estimate/", views.create_estimate_from_job, name="create_estimate_from_job"),
    path("jobs/<int:job_id>/create-invoice/", views.create_invoice_from_job, name="create_invoice_from_job"),

    # JOB MATERIALS
    path("jobs/<int:job_id>/materials/", views.job_material_list, name="job_material_list"),
    path("jobs/<int:job_id>/materials/add/", views.add_catalog_material_to_job, name="add_catalog_material_to_job"),
    path("jobs/materials/<int:material_id>/increase/", views.increase_job_material, name="increase_job_material"),
    path("jobs/materials/<int:material_id>/decrease/", views.decrease_job_material, name="decrease_job_material"),
    path("jobs/materials/<int:material_id>/delete/", views.delete_job_material, name="delete_job_material"),

    # ESTIMATES
    path("estimates/", views.estimates, name="estimates"),
    path("estimates/<int:estimate_id>/", views.estimate_detail, name="estimate_detail"),
    path("estimates/<int:estimate_id>/edit/", views.edit_estimate, name="edit_estimate"),
    path("estimates/<int:estimate_id>/approve/", views.approve_estimate, name="approve_estimate"),
    path("estimates/<int:estimate_id>/delete/", views.delete_estimate, name="delete_estimate"),

    # INVOICES
    path("invoices/", views.invoices, name="invoices"),
    path("invoices/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:invoice_id>/edit/", views.edit_invoice, name="edit_invoice"),
    path("invoices/<int:invoice_id>/add-payment/", views.add_payment, name="add_payment"),

    # TASKS
    path("tasks/", views.tasks, name="tasks"),
    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/complete/", views.complete_task, name="complete_task"),
]