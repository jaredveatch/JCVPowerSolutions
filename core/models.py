from django.db import models


class QuoteRequest(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    service = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CareerApplication(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, blank=True)
    license_info = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=50, choices=CUSTOMER_TYPE, default="residential")
    status = models.CharField(max_length=50, choices=STATUS, default="new")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="jobs")
    template = models.ForeignKey(ServiceTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150)
    status = models.CharField(max_length=50, choices=STATUS, default="new")
    job_address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    site_notes = models.TextField(blank=True)
    material_notes = models.TextField(blank=True)
    estimated_total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.title}"


class JobPhoto(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="job_photos/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo - {self.job.title}"


class Estimate(models.Model):
    STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="estimates")
    title = models.CharField(max_length=150)
    scope_of_work = models.TextField()
    exclusions = models.TextField(blank=True, default="Does not include unforeseen repairs, drywall repair, painting, utility fees, permit fees, or additional work outside the listed scope unless stated in writing.")
    terms = models.TextField(blank=True, default="Customer authorizes JCV Power Solutions to perform the listed work. Additional work, hidden conditions, code corrections, or customer-requested changes may result in additional charges.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS, default="draft")
    customer_signature_name = models.CharField(max_length=100, blank=True)
    signed_date = models.DateTimeField(null=True, blank=True)
    accepted_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Invoice(models.Model):
    STATUS = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    ]

    estimate = models.OneToOneField(Estimate, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=50, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default="draft")
    paid_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.invoice_number or f"Invoice for {self.estimate.title}"