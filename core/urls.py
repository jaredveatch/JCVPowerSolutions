from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("leads/", views.leads, name="leads"),
    path("leads/<int:lead_id>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:lead_id>/convert/", views.convert_lead, name="convert_lead"),

    path("customers/", views.customers, name="customers"),
    path("customers/create/", views.create_customer, name="create_customer"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:customer_id>/delete/", views.delete_customer, name="delete_customer"),

    path("customers/<int:customer_id>/create-job/", views.create_job, name="create_job"),

    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/create-estimate/", views.create_estimate_from_job, name="create_estimate_from_job"),
]