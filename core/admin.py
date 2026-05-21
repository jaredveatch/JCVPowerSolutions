from django.contrib import admin
from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    ServiceTemplate,
    Job,
    JobPhoto,
    Estimate,
    Invoice,
)


class JobPhotoInline(admin.TabularInline):
    model = JobPhoto
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "customer_type", "status", "created_at")
    list_filter = ("status", "customer_type", "city")
    search_fields = ("name", "phone", "email", "address", "city", "notes")


@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = ("icon", "name", "category", "default_labor_hours", "default_price", "active")
    list_filter = ("category", "active")
    search_fields = ("name", "category", "customer_description", "internal_checklist")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "template", "status", "estimated_total_price", "scheduled_date")
    list_filter = ("status", "template")
    search_fields = ("title", "customer__name", "customer__phone", "job_address", "description")
    inlines = [JobPhotoInline]

    fieldsets = (
        ("Job Info", {
            "fields": ("customer", "template", "title", "status", "job_address", "description")
        }),
        ("Field Notes", {
            "fields": ("site_notes", "material_notes")
        }),
        ("Money / Schedule", {
            "fields": ("estimated_total_price", "scheduled_date")
        }),
    )


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ("title", "job", "status", "total", "accepted_terms", "created_at")
    list_filter = ("status", "accepted_terms")
    search_fields = ("title", "job__customer__name", "scope_of_work")

    fieldsets = (
        ("Estimate Info", {
            "fields": ("job", "title", "status")
        }),
        ("Customer-Facing Scope", {
            "fields": ("scope_of_work", "exclusions", "terms")
        }),
        ("Totals", {
            "fields": ("subtotal", "tax", "total")
        }),
        ("Customer Acceptance / Signature", {
            "fields": ("customer_signature_name", "signed_date", "accepted_terms")
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "estimate", "amount_due", "due_date", "status", "paid_date")
    list_filter = ("status", "due_date")
    search_fields = ("invoice_number", "estimate__title", "estimate__job__customer__name")


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


admin.site.site_header = "JCV Power Solutions"
admin.site.site_title = "JCV Admin"
admin.site.index_title = "Business Dashboard"