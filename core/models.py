from decimal import Decimal

from django.db import models
from django.utils import timezone


# =========================================================
# LEADS / QUOTES
# =========================================================

class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("scheduled", "Scheduled"),
        ("quoted", "Quoted"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("converted", "Converted"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# CAREERS
# =========================================================

class CareerApplication(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    license_info = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# CUSTOMERS
# =========================================================

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("industrial", "Industrial"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("lead", "Lead"),
    ]

    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    customer_type = models.CharField(
        max_length=50,
        choices=CUSTOMER_TYPE_CHOICES,
        default="residential",
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active",
    )

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.company_name:
            return f"{self.name} - {self.company_name}"
        return self.name


# =========================================================
# SERVICE TEMPLATES
# =========================================================

class ServiceTemplate(models.Model):
    icon = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, blank=True, null=True)

    customer_description = models.TextField(blank=True, null=True)
    internal_checklist = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    default_labor_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    labor_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("110.00"),
    )

    estimated_material_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    material_markup = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.35"),
    )

    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    permit_required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    @property
    def labor_total(self):
        return Decimal(str(self.default_labor_hours or 0)) * Decimal(str(self.labor_rate or 0))

    @property
    def material_sell_price(self):
        return Decimal(str(self.estimated_material_cost or 0)) * Decimal(str(self.material_markup or 0))

    @property
    def calculated_price(self):
        return self.labor_total + self.material_sell_price

    def save(self, *args, **kwargs):
        self.default_price = self.calculated_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================================================
# MATERIAL CATALOG
# =========================================================

class MaterialCatalog(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    part_number = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    unit = models.CharField(max_length=50, default="each")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# SERVICE TEMPLATE MATERIALS
# =========================================================

class ServiceTemplateMaterial(models.Model):
    service_template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.CASCADE,
        related_name="template_materials",
    )

    material = models.ForeignKey(
        MaterialCatalog,
        on_delete=models.CASCADE,
        related_name="service_template_materials",
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        verbose_name = "Service Template Material"
        verbose_name_plural = "Service Template Materials"
        ordering = ["service_template__category", "service_template__name", "material__name"]
        unique_together = ("service_template", "material")

    @property
    def material_total(self):
        return Decimal(str(self.quantity or 0)) * Decimal(str(self.material.unit_cost or 0))

    @property
    def labor_total(self):
        return Decimal(str(self.quantity or 0)) * Decimal(str(self.material.labor_hours or 0))

    def __str__(self):
        return f"{self.service_template} - {self.material} x {self.quantity}"


# =========================================================
# JOBS
# =========================================================

class Job(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("site_visit", "Site Visit"),
        ("estimate_needed", "Estimate Needed"),
        ("estimate_sent", "Estimate Sent"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("waiting_parts", "Waiting on Parts"),
        ("completed", "Completed"),
        ("invoiced", "Invoiced"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="jobs",
    )

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="new")
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="normal")
    assigned_to = models.CharField(max_length=255, blank=True, null=True)

    job_address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    site_notes = models.TextField(blank=True, null=True)
    material_notes = models.TextField(blank=True, null=True)

    estimated_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def material_total(self):
        return sum(
            (item.material_total for item in self.job_materials.all()),
            Decimal("0.00"),
        )

    def labor_total(self):
        return sum(
            (item.labor_total for item in self.job_materials.all()),
            Decimal("0.00"),
        )

    def installed_total(self):
        return sum(
            (item.total_cost for item in self.job_materials.all()),
            Decimal("0.00"),
        )

    def save(self, *args, **kwargs):
        if self.template and not self.estimated_total_price:
            self.estimated_total_price = self.template.default_price

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# JOB MATERIALS
# =========================================================

class JobMaterial(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="job_materials",
    )

    material = models.ForeignKey(
        MaterialCatalog,
        on_delete=models.CASCADE,
        related_name="job_materials",
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    material_markup = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.35"),
    )

    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    labor_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("110.00"))

    material_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    material_sell_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sell_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Job Material"
        verbose_name_plural = "Job Materials"
        ordering = ["material__name"]

    def save(self, *args, **kwargs):
        quantity = Decimal(str(self.quantity or 0))

        if self.material:
            if not self.unit_cost:
                self.unit_cost = self.material.unit_cost

            if not self.labor_hours:
                self.labor_hours = self.material.labor_hours

        unit_cost = Decimal(str(self.unit_cost or 0))
        labor_hours = Decimal(str(self.labor_hours or 0))
        labor_rate = Decimal(str(self.labor_rate or 0))
        markup = Decimal(str(self.material_markup or 1))

        self.material_total = quantity * unit_cost
        self.material_sell_total = self.material_total * markup
        self.labor_total = quantity * labor_hours * labor_rate
        self.total_cost = self.material_total + self.labor_total
        self.sell_total = self.material_sell_total + self.labor_total

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job} - {self.material} x {self.quantity}"


# =========================================================
# JOB PHOTOS
# =========================================================

class JobPhoto(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(upload_to="job_photos/", blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job} - {self.caption or 'Photo'}"


# =========================================================
# ESTIMATES
# =========================================================

class Estimate(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="estimates",
    )

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    scope_of_work = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    customer_signature_name = models.CharField(max_length=255, blank=True, null=True)
    signed_date = models.DateTimeField(blank=True, null=True)
    accepted_terms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def recalculate_totals(self):
        self.subtotal = sum(
            (line.total for line in self.line_items.all()),
            Decimal("0.00"),
        )
        self.total = Decimal(str(self.subtotal or 0)) + Decimal(str(self.tax or 0))

    def save(self, *args, **kwargs):
        subtotal = Decimal(str(self.subtotal or 0))
        tax = Decimal(str(self.tax or 0))
        self.total = subtotal + tax
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# ESTIMATE LINE ITEMS
# =========================================================

class EstimateLineItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ("material", "Material"),
        ("labor", "Labor"),
        ("service", "Service"),
        ("fee", "Fee"),
        ("discount", "Discount"),
    ]

    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name="line_items",
    )

    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES,
        default="material",
    )

    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    source_job_material = models.ForeignKey(
        JobMaterial,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="estimate_line_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estimate Line Item"
        verbose_name_plural = "Estimate Line Items"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        quantity = Decimal(str(self.quantity or 0))
        unit_price = Decimal(str(self.unit_price or 0))

        self.total = quantity * unit_price
        super().save(*args, **kwargs)

        estimate = self.estimate
        estimate.subtotal = sum(
            (line.total for line in estimate.line_items.all()),
            Decimal("0.00"),
        )
        estimate.total = estimate.subtotal + Decimal(str(estimate.tax or 0))

        Estimate.objects.filter(id=estimate.id).update(
            subtotal=estimate.subtotal,
            total=estimate.total,
        )

    def __str__(self):
        return f"{self.estimate} - {self.description}"


# =========================================================
# INVOICES
# =========================================================

class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("partial", "Partially Paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    ]

    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="invoices",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="invoices",
    )

    invoice_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    due_date = models.DateField(blank=True, null=True)
    paid_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            latest_id = Invoice.objects.count() + 1
            self.invoice_number = f"JCV-{latest_id:05d}"

        subtotal = Decimal(str(self.subtotal or 0))
        tax = Decimal(str(self.tax or 0))
        amount_paid = Decimal(str(self.amount_paid or 0))

        self.total = subtotal + tax
        self.amount_due = self.total - amount_paid

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number or "Invoice"


# =========================================================
# PAYMENTS
# =========================================================

class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("check", "Check"),
        ("card", "Card"),
        ("ach", "ACH"),
        ("zelle", "Zelle"),
        ("other", "Other"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, default="cash")
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        invoice = self.invoice

        invoice.amount_paid = sum(
            (payment.amount for payment in invoice.payments.all()),
            Decimal("0.00"),
        )

        invoice.amount_due = invoice.total - invoice.amount_paid

        if invoice.amount_due <= 0:
            invoice.status = "paid"
            invoice.paid_date = timezone.now().date()
        elif invoice.amount_paid > 0:
            invoice.status = "partial"

        invoice.save()

    def __str__(self):
        return f"{self.invoice} - ${self.amount}"


# =========================================================
# JOB NOTES
# =========================================================

class JobNote(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    author = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField()
    internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job} - {self.author or 'Note'}"


# =========================================================
# AI SUGGESTIONS
# =========================================================

class AISuggestion(models.Model):
    CATEGORY_CHOICES = [
        ("estimate", "Estimate"),
        ("pricing", "Pricing"),
        ("materials", "Materials"),
        ("scope", "Scope of Work"),
        ("website", "Website Content"),
        ("service_template", "Service Template"),
        ("job", "Job"),
        ("general", "General"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("applied", "Applied"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="general")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    prompt = models.TextField(blank=True, null=True)
    suggestion = models.TextField()
    reason = models.TextField(blank=True, null=True)

    related_customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ai_suggestions",
    )

    related_job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ai_suggestions",
    )

    related_estimate = models.ForeignKey(
        Estimate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ai_suggestions",
    )

    related_service_template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ai_suggestions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI Suggestion"
        verbose_name_plural = "AI Suggestions"

    def approve(self):
        self.status = "approved"
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self):
        self.status = "rejected"
        self.reviewed_at = timezone.now()
        self.save()

    def mark_applied(self):
        self.status = "applied"
        self.reviewed_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title


# =========================================================
# TASKS
# =========================================================

class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=255)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tasks",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tasks",
    )

    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="normal")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    due_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date", "-created_at"]

    def __str__(self):
        return self.title