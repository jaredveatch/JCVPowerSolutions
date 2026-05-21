from django.contrib import admin
from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    Job,
    JobPhoto,
)


class JobPhotoInline(admin.TabularInline):
    model = JobPhoto
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "customer_type", "lead_status", "created_at")
    list_filter = ("lead_status", "customer_type", "city", "created_at")
    search_fields = ("name", "phone", "email", "address", "city", "notes")
    ordering = ("-created_at",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "job_type",
        "status",
        "site_visit_date",
        "quote_due_date",
        "estimated_total_price",
        "updated_at",
    )

    list_filter = ("status", "job_type", "site_visit_date", "quote_due_date")
    search_fields = (
        "title",
        "customer__name",
        "customer__phone",
        "job_address",
        "description",
        "internal_notes",
    )

    inlines = [JobPhotoInline]

    fieldsets = (
        ("Customer / Job Info", {
            "fields": (
                "customer",
                "title",
                "job_type",
                "status",
                "job_address",
                "description",
            )
        }),
        ("Scheduling", {
            "fields": (
                "site_visit_date",
                "quote_due_date",
            )
        }),
        ("Site Visit Notes", {
            "fields": (
                "labor_notes",
                "material_notes",
                "code_notes",
                "access_notes",
            )
        }),
        ("Quote Estimate", {
            "fields": (
                "estimated_labor_hours",
                "estimated_material_cost",
                "estimated_total_price",
            )
        }),
        ("Internal Notes", {
            "fields": (
                "internal_notes",
            )
        }),
    )


@admin.register(JobPhoto)
class JobPhotoAdmin(admin.ModelAdmin):
    list_display = ("job", "caption", "uploaded_at")
    search_fields = ("job__title", "caption", "notes")


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "service", "created_at")
    list_filter = ("service", "created_at")
    search_fields = ("name", "phone", "email", "service", "message")


@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "position", "experience", "created_at")
    list_filter = ("position", "created_at")
    search_fields = ("name", "phone", "email", "position", "experience", "license_info", "message")