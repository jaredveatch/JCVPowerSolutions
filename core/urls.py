from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("leads/", views.leads, name="leads"),
    path("leads/<int:lead_id>/", views.lead_detail, name="lead_detail"),

    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),

    path("estimates/", views.estimates, name="estimates"),
]