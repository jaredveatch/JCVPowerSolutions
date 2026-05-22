from django.urls import path
from . import views

urlpatterns = [
    # WEBSITE
    path("", views.home, name="home"),

    # DASHBOARD
    path("dashboard/", views.dashboard, name="dashboard"),

    # LEADS
    path("leads/", views.leads, name="leads"),
    path("leads/<int:lead_id>/", views.lead_detail, name="lead_detail"),

    # JOBS
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),

    # ESTIMATES
    path("estimates/", views.estimates, name="estimates"),
]