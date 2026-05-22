from django.db import models
from django.utils import timezone


# =========================================================
# QUOTE REQUESTS / LEADS
# =========================================================

class QuoteRequest(models.Model):

    STATUS = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
        ("lost", "Lost"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    service = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default="new")
    source = models.CharField(max_length=100, blank=True, default="Website")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# CAREERS
# =========================================================

class CareerApplication(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, blank=True)
    license_info = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# CUSTOMERS
# =========================================================

class Customer(models.Model):

    CUSTOMER_TYPE = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("industrial", "Industrial"),
    ]

    STATUS = [
        ("new", "New"),
        ("active", "Active"),
        ("estimate_sent", "Estimate Sent"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("paid", "Paid"),
    ]

    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=50, choices=CUSTOMER_TYPE, default="residential")
    status = models.CharField(max_length=50, choices=STATUS, default="new")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.name}"
        return self.name


# =========================================================
# SERVICE TEMPLATES / FLAT RATE ITEMS
# =========================================================

class ServiceTemplate(models.Model):

    name = models.CharField(max_length=150)
    icon = models.CharField(max_length=10, default="⚡")
    category = models.CharField(max_length=100, default="Residential Service")

    customer_description = models.TextField(
        help_text="This is what the customer sees on the estimate."
    )

    internal_checklist = models.TextField(
        blank=True,
        help_text="Private material checklist, code notes, permits, utility notes, tools, etc."
    )

    default_labor_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================================================
# JOBS
# =========================================================

class Job(models.Model):

    STATUS = [
        ("new", "New"),
        ("site_visit", "Site Visit"),
        ("estimate_needed", "Estimate Needed"),
        ("estimate_sent", "Estimate Sent"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("invoiced", "Invoiced"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=150)
    status = models.CharField(max_length=50, choices=STATUS, default="new")
    priority = models.CharField(max_length=50, choices=PRIORITY, default="normal")

    job_address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    site_notes = models.TextField(blank=True)
    material_notes = models.TextField(blank=True)

    estimated_total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    assigned_to = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.title}"


# =========================================================
# JOB PHOTOS
# =========================================================

class JobPhoto(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="photos"
    )

    image = models.ImageField(upload_to="job_photos/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo - {self.job.title}"


# =========================================================
# ESTIMATES
# =========================================================

class Estimate(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="estimates"
    )

    title = models.CharField(max_length=150)
    scope_of_work = models.TextField()

    exclusions = models.TextField(
        blank=True,
        default="Does not include unforeseen repairs, drywall repair, painting, utility fees, permit fees, or additional work outside the listed scope unless stated in writing."
    )

    terms = models.TextField(
        blank=True,
        default="Customer authorizes JCV Power Solutions to perform the listed work. Additional work, hidden conditions, code corrections, or customer-requested changes may result in additional charges."
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=50, choices=STATUS, default="draft")

    customer_signature_name = models.CharField(max_length=100, blank=True)
    signed_date = models.DateTimeField(null=True, blank=True)
    accepted_terms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = self.subtotal + self.tax
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# INVOICES
# =========================================================

class Invoice(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("partial", "Partially Paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("void", "Void"),
    ]

    estimate = models.OneToOneField(
        Estimate,
        on_delete=models.CASCADE,
        related_name="invoice",
        null=True,
        blank=True
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="invoices",
        null=True,
        blank=True
    )

    invoice_number = models.CharField(max_length=50, blank=True)

    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default="draft")
    paid_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = self.subtotal + self.tax
        self.amount_due = self.total - self.amount_paid

        if self.amount_due <= 0 and self.total > 0:
            self.status = "paid"
            if not self.paid_date:
                self.paid_date = timezone.now().date()
        elif self.amount_paid > 0:
            self.status = "partial"

        super().save(*args, **kwargs)

        if not self.invoice_number:
            self.invoice_number = f"INV-{self.id:06d}"
            super().save(update_fields=["invoice_number"])

    def __str__(self):
        return self.invoice_number or f"Invoice #{self.id}"


# =========================================================
# PAYMENTS
# =========================================================

class Payment(models.Model):

    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("check", "Check"),
        ("card", "Card"),
        ("ach", "ACH"),
        ("other", "Other"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default="card"
    )

    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        invoice = self.invoice
        invoice.amount_paid = sum(payment.amount for payment in invoice.payments.all())
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
        related_name="notes"
    )

    author = models.CharField(max_length=100, blank=True)
    note = models.TextField()
    internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.job.title}"


# =========================================================
# TASKS / FOLLOW UPS
# =========================================================

class Task(models.Model):

    STATUS = [
        ("open", "Open"),
        ("completed", "Completed"),
    ]

    PRIORITY = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    title = models.CharField(max_length=200)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True
    )

    assigned_to = models.CharField(max_length=100, blank=True)

    due_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default="open")
    priority = models.CharField(max_length=20, choices=PRIORITY, default="normal")

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title