from django.shortcuts import render
from django.http import JsonResponse
from .models import QuoteRequest, CareerApplication


def home(request):
    if request.method == "POST":

        if "quote_form" in request.POST:
            QuoteRequest.objects.create(
                name=request.POST.get("name"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                service=request.POST.get("service"),
                message=request.POST.get("message"),
            )
            return JsonResponse({
                "success": True,
                "message": "Thank you for submitting your request. We will contact you soon."
            })

        if "career_form" in request.POST:
            CareerApplication.objects.create(
                name=request.POST.get("applicant_name"),
                phone=request.POST.get("applicant_phone"),
                email=request.POST.get("applicant_email"),
                position=request.POST.get("position"),
                experience=request.POST.get("experience"),
                license_info=request.POST.get("license"),
                message=request.POST.get("career_message"),
            )
            return JsonResponse({
                "success": True,
                "message": "Thank you for submitting your application. We will review it soon."
            })

    context = {}

    if request.user.is_authenticated and request.user.is_staff:
        context["quote_requests"] = QuoteRequest.objects.all().order_by("-created_at")
        context["career_applications"] = CareerApplication.objects.all().order_by("-created_at")

    return render(request, "home.html", context)