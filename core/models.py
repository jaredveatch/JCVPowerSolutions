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
    LEAD_STATUS_CHOICES = [
        ("new_lead", "New Lead"),
        ("contacted", "Contacted"),
        ("estimate_scheduled", "Estimate Scheduled"),
        ("estimate_sent", "Estimate Sent"),
        ("approved", "Approved"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("paid", "Paid"),
        ("lost", "Lost / Did Not Book"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(
        max_length=50,
        choices=[
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            ("industrial", "Industrial"),
        ],
        default="residential",
    )

    lead_status = models.CharField(
        max_length=50,
        choices=LEAD_STATUS_CHOICES,
        default="new_lead",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_STATUS_CHOICES = [
        ("new", "New"),
        ("site_visit_scheduled", "Site Visit Scheduled"),
        ("site_visit_completed", "Site Visit Completed"),
        ("quote_needed", "Quote Needed"),
        ("quote_sent", "Quote Sent"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("invoiced", "Invoiced"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    JOB_TYPE_CHOICES = [
        ("service_call", "Service Call"),
        ("panel_upgrade", "Panel / Service Upgrade"),
        ("lighting", "Lighting"),
        ("troubleshooting", "Troubleshooting"),
        ("new_install", "New Installation"),
        ("commercial", "Commercial Work"),
        ("industrial", "Industrial Work"),
        ("other", "Other"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="jobs")

    title = models.CharField(max_length=150)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default="service_call")
    status = models.CharField(max_length=50, choices=JOB_STATUS_CHOICES, default="new")

    job_address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    site_visit_date = models.DateTimeField(null=True, blank=True)
    quote_due_date = models.DateField(null=True, blank=True)

    labor_notes = models.TextField(blank=True)
    material_notes = models.TextField(blank=True)
    code_notes = models.TextField(blank=True)
    access_notes = models.TextField(blank=True)

    estimated_labor_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    estimated_material_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    internal_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - {self.title}"


class JobPhoto(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="job_photos/")
    caption = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.job.title}"