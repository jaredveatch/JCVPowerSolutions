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
    EstimateLineItem,
    Invoice,
    Payment,
    JobNote,
    Task,
    AISuggestion,
    AICommand,
    AICodeChange,
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
        "material_sell_total",
        "labor_total",
        "total_cost",
        "sell_total",
    )
    fields = (
        "material",
        "quantity",
        "unit_cost",
        "material_markup",
        "labor_hours",
        "labor_rate",
        "material_total",
        "material_sell_total",
        "labor_total",
        "total_cost",
        "sell_total",
    )


class EstimateLineItemInline(admin.TabularInline):
    model = EstimateLineItem
    extra = 1
    readonly_fields = ("total",)
    fields = (
        "item_type",
        "description",
        "quantity",
        "unit_price",
        "total",
        "source_job_material",
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


class AICodeChangeInline(admin.TabularInline):
    model = AICodeChange
    extra = 0
    readonly_fields = (
        "file_path",
        "action",
        "status",
        "notes",
        "error",
        "created_at",
        "applied_at",
    )
    fields = (
        "file_path",
        "action",
        "status",
        "notes",
        "error",
        "created_at",
        "applied_at",
    )
    can_delete = False


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
    list_filter = ("status", "service", "source", "created_at")
    search_fields = ("name", "phone", "email", "service", "message")
    ordering = ("-created_at",)


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
        "created_at",
    )
    list_filter = ("position", "created_at")
    search_fields = (
        "name",
        "phone",
        "email",
        "position",
        "experience",
        "license_info",
        "message",
    )
    ordering = ("-created_at",)


# =========================================================
# CUSTOMERS
# =========================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_name",
        "phone",
        "email",
        "city",
        "customer_type",
        "status",
        "created_at",
    )
    list_filter = ("status", "customer_type", "city", "created_at")
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
            "fields": ("notes",)
        }),
    )
    inlines = [TaskInline]
    ordering = ("-created_at",)


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
        "labor_rate",
        "estimated_material_cost",
        "material_markup",
        "default_price",
        "permit_required",
        "active",
    )
    list_filter = ("category", "active", "permit_required")
    search_fields = (
        "name",
        "category",
        "customer_description",
        "internal_checklist",
        "notes",
    )
    fieldsets = (
        ("Template Info", {
            "fields": (
                "icon",
                "name",
                "category",
                "active",
            )
        }),
        ("Customer-Facing Details", {
            "fields": (
                "customer_description",
            )
        }),
        ("Internal Details", {
            "fields": (
                "internal_checklist",
                "notes",
                "permit_required",
            )
        }),
        ("Pricing", {
            "fields": (
                "default_labor_hours",
                "labor_rate",
                "estimated_material_cost",
                "material_markup",
                "default_price",
            )
        }),
    )
    inlines = [ServiceTemplateMaterialInline]
    ordering = ("category", "name")


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
    list_filter = ("active", "manufacturer")
    search_fields = ("name", "manufacturer", "part_number", "description")
    ordering = ("name",)


@admin.register(ServiceTemplateMaterial)
class ServiceTemplateMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "service_template",
        "material",
        "quantity",
    )
    list_filter = ("service_template__category", "service_template")
    search_fields = ("service_template__name", "material__name")
    ordering = (
        "service_template__category",
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
    ordering = ("-created_at",)


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
        "material_markup",
        "labor_hours",
        "labor_rate",
        "material_total",
        "material_sell_total",
        "labor_total",
        "total_cost",
        "sell_total",
    )
    list_filter = ("material", "labor_rate", "material_markup")
    search_fields = (
        "job__title",
        "job__customer__name",
        "material__name",
    )
    readonly_fields = (
        "material_total",
        "material_sell_total",
        "labor_total",
        "total_cost",
        "sell_total",
    )
    ordering = ("job", "material__name")


# =========================================================
# JOB PHOTOS
# =========================================================

@admin.register(JobPhoto)
class JobPhotoAdmin(admin.ModelAdmin):
    list_display = ("job", "caption", "uploaded_at")
    search_fields = ("job__title", "job__customer__name", "caption")
    ordering = ("-uploaded_at",)


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
    list_filter = ("status", "accepted_terms", "created_at")
    search_fields = (
        "title",
        "job__title",
        "job__customer__name",
        "scope_of_work",
    )
    readonly_fields = ("total",)
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
    inlines = [EstimateLineItemInline]
    ordering = ("-created_at",)


@admin.register(EstimateLineItem)
class EstimateLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "estimate",
        "item_type",
        "description",
        "quantity",
        "unit_price",
        "total",
    )
    list_filter = ("item_type", "estimate__status")
    search_fields = (
        "estimate__title",
        "estimate__job__title",
        "estimate__job__customer__name",
        "description",
    )
    readonly_fields = ("total",)
    ordering = ("estimate", "id")


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
    list_filter = ("status", "due_date", "paid_date", "created_at")
    search_fields = (
        "invoice_number",
        "title",
        "description",
        "estimate__title",
        "estimate__job__customer__name",
        "job__title",
        "job__customer__name",
    )
    readonly_fields = ("total", "amount_due")
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
    inlines = [PaymentInline]
    ordering = ("-created_at",)


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
    list_filter = ("method", "paid_at")
    search_fields = ("invoice__invoice_number", "reference", "notes")
    ordering = ("-paid_at",)


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
    list_filter = ("internal", "created_at")
    search_fields = ("job__title", "job__customer__name", "author", "note")
    ordering = ("-created_at",)


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
    ordering = ("status", "due_date", "-created_at")


# =========================================================
# AI SUGGESTIONS
# =========================================================

@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "related_customer",
        "related_job",
        "related_estimate",
        "related_service_template",
        "created_at",
        "reviewed_at",
        "applied_at",
    )
    list_filter = (
        "category",
        "status",
        "created_at",
        "reviewed_at",
        "applied_at",
    )
    search_fields = (
        "title",
        "prompt",
        "suggestion",
        "reason",
    )
    readonly_fields = (
        "created_at",
    )
    fieldsets = (
        ("Suggestion", {
            "fields": (
                "title",
                "category",
                "status",
                "reason",
            )
        }),
        ("AI Content", {
            "fields": (
                "prompt",
                "suggestion",
            )
        }),
        ("Related Records", {
            "fields": (
                "related_customer",
                "related_job",
                "related_estimate",
                "related_service_template",
            )
        }),
        ("Action Payload", {
            "fields": (
                "action_type",
                "action_payload",
            )
        }),
        ("Dates", {
            "fields": (
                "created_at",
                "reviewed_at",
                "applied_at",
            )
        }),
    )
    ordering = ("-created_at",)


# =========================================================
# AI COMMANDS
# =========================================================

@admin.register(AICommand)
class AICommandAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "created_at",
        "generated_at",
        "applied_at",
        "pushed_at",
    )
    list_filter = (
        "status",
        "created_at",
        "generated_at",
        "applied_at",
        "pushed_at",
    )
    search_fields = (
        "title",
        "prompt",
        "summary",
        "log",
    )
    readonly_fields = (
        "created_at",
        "generated_at",
        "applied_at",
        "pushed_at",
    )
    fieldsets = (
        ("Command", {
            "fields": (
                "title",
                "prompt",
                "summary",
                "status",
            )
        }),
        ("Log", {
            "fields": (
                "log",
            )
        }),
        ("Dates", {
            "fields": (
                "created_at",
                "generated_at",
                "applied_at",
                "pushed_at",
            )
        }),
    )
    inlines = [AICodeChangeInline]
    ordering = ("-created_at",)


# =========================================================
# AI CODE CHANGES
# =========================================================

@admin.register(AICodeChange)
class AICodeChangeAdmin(admin.ModelAdmin):
    list_display = (
        "command",
        "file_path",
        "action",
        "status",
        "created_at",
        "applied_at",
    )
    list_filter = (
        "action",
        "status",
        "created_at",
        "applied_at",
    )
    search_fields = (
        "command__title",
        "file_path",
        "notes",
        "original_content",
        "proposed_content",
        "error",
    )
    readonly_fields = (
        "created_at",
        "applied_at",
    )
    fieldsets = (
        ("Code Change", {
            "fields": (
                "command",
                "file_path",
                "action",
                "status",
                "notes",
            )
        }),
        ("Content", {
            "fields": (
                "original_content",
                "proposed_content",
            )
        }),
        ("Error / Dates", {
            "fields": (
                "error",
                "created_at",
                "applied_at",
            )
        }),
    )
    ordering = ("command", "file_path")


# =========================================================
# ADMIN BRANDING
# =========================================================

admin.site.site_header = "JCV Power Solutions"
admin.site.site_title = "JCV Admin"
admin.site.index_title = "JCV Command Center"