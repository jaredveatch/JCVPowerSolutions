from django.contrib import admin

from .models import (
    QuoteRequest,
    CareerApplication,
    Customer,
    ServiceTemplate,
    MaterialCatalog,
    ServiceTemplateMaterial,
    Job,
    JobMaterial,
    JobPhoto,
    Estimate,
    Invoice,
    Payment,
    JobNote,
    Task,
)


# =========================================================
# INLINES
# =========================================================

class ServiceTemplateMaterialInline(admin.TabularInline):
    model = ServiceTemplateMaterial
    extra = 1


class JobMaterialInline(admin.TabularInline):
    model = JobMaterial
    extra = 1

    readonly_fields = (
        "material_total",
        "labor_total",
        "total_cost",
    )

    fields = (
        "material",
        "quantity",
        "unit_cost",
        "labor_hours",
        "labor_rate",
        "material_total",
        "labor_total",
        "total_cost",
    )


class JobPhotoInline(admin.TabularInline):
    model = JobPhoto
    extra = 1


class JobNoteInline(admin.TabularInline):
    model = JobNote
    extra = 0


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


# =========================================================
# LEADS / QUOTES
# =========================================================

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "service",
        "status",
        "source",
        "created_at",
    )

    list_filter = (
        "status",
        "service",
        "source",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "service",
        "message",
    )


# =========================================================
# CAREERS
# =========================================================

@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "position",
        "experience",
        "created_at",
    )

    list_filter = (
        "position",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "position",
        "experience",
        "license_info",
        "message",
    )


# =========================================================
# CUSTOMERS
# =========================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_name",
        "phone",
        "city",
        "customer_type",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "customer_type",
        "city",
        "created_at",
    )

    search_fields = (
        "name",
        "company_name",
        "phone",
        "email",
        "address",
        "city",
        "notes",
    )

    fieldsets = (
        ("Customer Info", {
            "fields": (
                "name",
                "company_name",
                "phone",
                "email",
                "customer_type",
                "status",
            )
        }),
        ("Address", {
            "fields": (
                "address",
                "city",
            )
        }),
        ("Notes", {
            "fields": (
                "notes",
            )
        }),
    )

    inlines = [
        TaskInline,
    ]


# =========================================================
# SERVICE TEMPLATES
# =========================================================

@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "icon",
        "name",
        "category",
        "default_labor_hours",
        "default_price",
        "active",
    )

    list_filter = (
        "category",
        "active",
    )

    search_fields = (
        "name",
        "category",
        "customer_description",
        "internal_checklist",
    )

    inlines = [
        ServiceTemplateMaterialInline,
    ]


# =========================================================
# MATERIAL CATALOG
# =========================================================

@admin.register(MaterialCatalog)
class MaterialCatalogAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "manufacturer",
        "part_number",
        "unit",
        "unit_cost",
        "labor_hours",
        "active",
    )

    list_filter = (
        "active",
        "manufacturer",
    )

    search_fields = (
        "name",
        "manufacturer",
        "part_number",
        "description",
    )


@admin.register(ServiceTemplateMaterial)
class ServiceTemplateMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "service_template",
        "material",
        "quantity",
    )

    search_fields = (
        "service_template__name",
        "material__name",
    )


# =========================================================
# JOBS
# =========================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "template",
        "status",
        "priority",
        "assigned_to",
        "estimated_total_price",
        "scheduled_date",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "template",
        "assigned_to",
        "scheduled_date",
        "created_at",
    )

    search_fields = (
        "title",
        "customer__name",
        "customer__phone",
        "job_address",
        "description",
        "site_notes",
        "material_notes",
    )

    fieldsets = (
        ("Job Info", {
            "fields": (
                "customer",
                "template",
                "title",
                "status",
                "priority",
                "assigned_to",
                "job_address",
                "description",
            )
        }),
        ("Field Notes", {
            "fields": (
                "site_notes",
                "material_notes",
            )
        }),
        ("Money / Schedule", {
            "fields": (
                "estimated_total_price",
                "scheduled_date",
                "completed_at",
            )
        }),
    )

    inlines = [
        JobMaterialInline,
        JobPhotoInline,
        JobNoteInline,
        TaskInline,
    ]


# =========================================================
# JOB MATERIALS
# =========================================================

@admin.register(JobMaterial)
class JobMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "material",
        "quantity",
        "unit_cost",
        "labor_hours",
        "labor_rate",
        "material_total",
        "labor_total",
        "total_cost",
    )

    list_filter = (
        "material",
        "labor_rate",
    )

    search_fields = (
        "job__title",
        "job__customer__name",
        "material__name",
    )

    readonly_fields = (
        "material_total",
        "labor_total",
        "total_cost",
    )


# =========================================================
# JOB PHOTOS
# =========================================================

@admin.register(JobPhoto)
class JobPhotoAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "caption",
        "uploaded_at",
    )

    search_fields = (
        "job__title",
        "job__customer__name",
        "caption",
    )


# =========================================================
# ESTIMATES
# =========================================================

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "job",
        "status",
        "subtotal",
        "tax",
        "total",
        "accepted_terms",
        "created_at",
    )

    list_filter = (
        "status",
        "accepted_terms",
        "created_at",
    )

    search_fields = (
        "title",
        "job__title",
        "job__customer__name",
        "scope_of_work",
    )

    fieldsets = (
        ("Estimate Info", {
            "fields": (
                "job",
                "title",
                "status",
            )
        }),
        ("Customer-Facing Scope", {
            "fields": (
                "scope_of_work",
                "exclusions",
                "terms",
            )
        }),
        ("Totals", {
            "fields": (
                "subtotal",
                "tax",
                "total",
            )
        }),
        ("Customer Acceptance / Signature", {
            "fields": (
                "customer_signature_name",
                "signed_date",
                "accepted_terms",
            )
        }),
    )


# =========================================================
# INVOICES
# =========================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "estimate",
        "job",
        "status",
        "subtotal",
        "tax",
        "total",
        "amount_paid",
        "amount_due",
        "due_date",
        "paid_date",
    )

    list_filter = (
        "status",
        "due_date",
        "paid_date",
        "created_at",
    )

    search_fields = (
        "invoice_number",
        "title",
        "description",
        "estimate__title",
        "estimate__job__customer__name",
        "job__title",
        "job__customer__name",
    )

    fieldsets = (
        ("Invoice Info", {
            "fields": (
                "estimate",
                "job",
                "invoice_number",
                "title",
                "description",
                "status",
            )
        }),
        ("Totals", {
            "fields": (
                "subtotal",
                "tax",
                "total",
                "amount_paid",
                "amount_due",
            )
        }),
        ("Dates", {
            "fields": (
                "due_date",
                "paid_date",
            )
        }),
    )

    inlines = [
        PaymentInline,
    ]


# =========================================================
# PAYMENTS
# =========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "amount",
        "method",
        "reference",
        "paid_at",
    )

    list_filter = (
        "method",
        "paid_at",
    )

    search_fields = (
        "invoice__invoice_number",
        "reference",
        "notes",
    )


# =========================================================
# JOB NOTES
# =========================================================

@admin.register(JobNote)
class JobNoteAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "author",
        "internal",
        "created_at",
    )

    list_filter = (
        "internal",
        "created_at",
    )

    search_fields = (
        "job__title",
        "job__customer__name",
        "author",
        "note",
    )


# =========================================================
# TASKS
# =========================================================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "job",
        "assigned_to",
        "priority",
        "status",
        "due_date",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "assigned_to",
        "due_date",
        "created_at",
    )

    search_fields = (
        "title",
        "customer__name",
        "customer__phone",
        "job__title",
        "assigned_to",
        "notes",
    )


# =========================================================
# ADMIN BRANDING
# =========================================================

admin.site.site_header = "JCV Power Solutions"
admin.site.site_title = "JCV Admin"
admin.site.index_title = "Business Dashboard"