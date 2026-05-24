from django.contrib import admin, messages

from core.services.ai_apply_engine import apply_ai_suggestion

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
)


# =========================================================
# INLINES
# =========================================================

class ServiceTemplateMaterialInline(admin.TabularInline):
    model = ServiceTemplateMaterial
    extra = 1
    readonly_fields = ("material_total", "labor_total")
    fields = ("material", "quantity", "material_total", "labor_total")


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
            "fields": ("address", "city")
        }),
        ("Notes", {
            "fields": ("notes",)
        }),
    )

    inlines = [TaskInline]


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
        "labor_total_display",
        "material_sell_price_display",
        "calculated_price_display",
        "default_price",
        "permit_required",
        "active",
    )

    list_filter = (
        "category",
        "permit_required",
        "active",
    )

    search_fields = (
        "name",
        "category",
        "customer_description",
        "internal_checklist",
        "notes",
    )

    list_editable = (
        "default_labor_hours",
        "labor_rate",
        "estimated_material_cost",
        "material_markup",
        "permit_required",
        "active",
    )

    readonly_fields = (
        "labor_total_display",
        "material_sell_price_display",
        "calculated_price_display",
        "default_price",
        "created_at",
    )

    fieldsets = (
        ("Service Info", {
            "fields": (
                "icon",
                "name",
                "category",
                "active",
                "permit_required",
            )
        }),
        ("Customer / Internal Notes", {
            "fields": (
                "customer_description",
                "internal_checklist",
                "notes",
            )
        }),
        ("Labor Pricing", {
            "fields": (
                "default_labor_hours",
                "labor_rate",
                "labor_total_display",
            )
        }),
        ("Material Pricing", {
            "fields": (
                "estimated_material_cost",
                "material_markup",
                "material_sell_price_display",
            )
        }),
        ("Calculated Sell Price", {
            "fields": (
                "calculated_price_display",
                "default_price",
            )
        }),
        ("System", {
            "fields": ("created_at",)
        }),
    )

    ordering = ("category", "name")
    inlines = [ServiceTemplateMaterialInline]

    def labor_total_display(self, obj):
        return f"${obj.labor_total:,.2f}"

    labor_total_display.short_description = "Labor Total"

    def material_sell_price_display(self, obj):
        return f"${obj.material_sell_price:,.2f}"

    material_sell_price_display.short_description = "Material Sell Price"

    def calculated_price_display(self, obj):
        return f"${obj.calculated_price:,.2f}"

    calculated_price_display.short_description = "Calculated Price"


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
    list_editable = ("unit_cost", "labor_hours", "active")
    ordering = ("name",)


@admin.register(ServiceTemplateMaterial)
class ServiceTemplateMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "service_template",
        "material",
        "quantity",
        "material_total_display",
        "labor_total_display",
    )
    list_filter = (
        "service_template__category",
        "service_template",
    )
    search_fields = (
        "service_template__name",
        "material__name",
    )
    ordering = (
        "service_template__category",
        "service_template__name",
        "material__name",
    )

    def material_total_display(self, obj):
        return f"${obj.material_total:,.2f}"

    material_total_display.short_description = "Material Cost"

    def labor_total_display(self, obj):
        return f"{obj.labor_total:,.2f} hrs"

    labor_total_display.short_description = "Labor Hours"


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
        "material_total_display",
        "labor_total_display",
        "installed_total_display",
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

    readonly_fields = (
        "material_total_display",
        "labor_total_display",
        "installed_total_display",
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
                "material_total_display",
                "labor_total_display",
                "installed_total_display",
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

    def material_total_display(self, obj):
        return f"${obj.material_total():,.2f}"

    material_total_display.short_description = "Material Cost"

    def labor_total_display(self, obj):
        return f"${obj.labor_total():,.2f}"

    labor_total_display.short_description = "Labor Total"

    def installed_total_display(self, obj):
        return f"${obj.installed_total():,.2f}"

    installed_total_display.short_description = "Installed Cost"


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
        "material_total",
        "material_sell_total",
        "labor_hours",
        "labor_rate",
        "labor_total",
        "total_cost",
        "sell_total",
    )

    list_filter = (
        "material",
        "labor_rate",
        "material_markup",
    )

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

    ordering = (
        "job",
        "material__name",
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

    list_filter = (
        "item_type",
        "estimate__status",
    )

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

    readonly_fields = (
        "total",
        "amount_due",
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

    inlines = [PaymentInline]


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
# AI SUGGESTIONS
# =========================================================

@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "action_type",
        "related_customer",
        "related_job",
        "related_estimate",
        "related_service_template",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "action_type",
        "created_at",
    )

    search_fields = (
        "title",
        "prompt",
        "suggestion",
        "reason",
        "action_type",
        "related_customer__name",
        "related_job__title",
        "related_estimate__title",
        "related_service_template__name",
    )

    readonly_fields = (
        "created_at",
        "reviewed_at",
    )

    fieldsets = (
        ("Suggestion", {
            "fields": (
                "title",
                "category",
                "status",
                "prompt",
                "suggestion",
                "reason",
            )
        }),
        ("Apply Engine", {
            "fields": (
                "action_type",
                "action_payload",
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
        ("Review Dates", {
            "fields": (
                "created_at",
                "reviewed_at",
            )
        }),
    )

    actions = (
        "approve_suggestions",
        "reject_suggestions",
        "mark_suggestions_applied",
        "apply_selected_ai_suggestions",
    )

    def approve_suggestions(self, request, queryset):
        for suggestion in queryset:
            suggestion.approve()

        self.message_user(
            request,
            f"Approved {queryset.count()} AI suggestion(s).",
            messages.SUCCESS,
        )

    approve_suggestions.short_description = "Approve selected AI suggestions"

    def reject_suggestions(self, request, queryset):
        for suggestion in queryset:
            suggestion.reject()

        self.message_user(
            request,
            f"Rejected {queryset.count()} AI suggestion(s).",
            messages.SUCCESS,
        )

    reject_suggestions.short_description = "Reject selected AI suggestions"

    def mark_suggestions_applied(self, request, queryset):
        for suggestion in queryset:
            suggestion.mark_applied()

        self.message_user(
            request,
            f"Marked {queryset.count()} AI suggestion(s) as applied.",
            messages.SUCCESS,
        )

    mark_suggestions_applied.short_description = "Mark selected AI suggestions as applied"

    def apply_selected_ai_suggestions(self, request, queryset):
        applied_count = 0

        for suggestion in queryset:
            try:
                apply_ai_suggestion(suggestion.id)
                applied_count += 1
            except Exception as error:
                self.message_user(
                    request,
                    f"Could not apply '{suggestion.title}': {error}",
                    messages.ERROR,
                )

        self.message_user(
            request,
            f"Applied {applied_count} AI suggestion(s).",
            messages.SUCCESS,
        )

    apply_selected_ai_suggestions.short_description = "Apply selected AI suggestions"


# =========================================================
# ADMIN BRANDING
# =========================================================

admin.site.site_header = "JCV Power Solutions"
admin.site.site_title = "JCV Admin"
admin.site.index_title = "Business Dashboard"