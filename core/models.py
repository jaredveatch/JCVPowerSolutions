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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="active")
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
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    customer_description = models.TextField(blank=True, null=True)
    internal_checklist = models.TextField(blank=True, null=True)
    default_labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

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
    labor_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"

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

    def __str__(self):
        return f"{self.service_template} - {self.material} x {self.quantity}"


# =========================================================
# JOBS
# =========================================================

class Job(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("waiting_parts", "Waiting on Parts"),
        ("completed", "Completed"),
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
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Job Material"
        verbose_name_plural = "Job Materials"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
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

    def __str__(self):
        return self.title


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
        related_name="invoices",
    )

    invoice_number = models.CharField(max_length=100, unique=True)
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

    def save(self, *args, **kwargs):
        self.amount_due = self.total - self.amount_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


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

    def __str__(self):
        return f"{self.job} - {self.author or 'Note'}"


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

    def __str__(self):
        return self.title