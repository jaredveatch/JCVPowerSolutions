from django.core.management.base import BaseCommand

from core.models import ServiceTemplate


MASTER_TEMPLATE_NAMES = [
    "Diagnostic & Troubleshooting",
    "Panel & Service Upgrades",
    "Grounding & Bonding",
    "Dedicated Circuits",
    "EV Charger Installation",
    "Generator & Backup Power",
    "Receptacles & Power Devices",
    "Switches & Controls",
    "Lighting Installation & Repair",
    "Recessed Lighting",
    "Ceiling Fans & Ventilation",
    "Smoke & Life Safety",
    "Smart Home Electrical",
    "Low Voltage & Communications",
    "Exterior Electrical",
    "Landscape & Specialty Lighting",
    "Appliance Connections",
    "Pools, Spas & Outdoor Equipment",
    "Remodels & Additions",
    "Wiring Repairs & Rewiring",
    "Code Corrections",
    "Home Electrical Inspections",
    "Surge Protection",
    "Permit & Utility Coordination",
    "Custom Electrical Work",
]


class Command(BaseCommand):
    help = "Deactivate legacy templates and keep only the 25 residential master templates active."

    def handle(self, *args, **kwargs):
        inactive_count = ServiceTemplate.objects.exclude(
            name__in=MASTER_TEMPLATE_NAMES
        ).update(active=False)

        active_count = ServiceTemplate.objects.filter(
            name__in=MASTER_TEMPLATE_NAMES
        ).update(active=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Activated {active_count} master templates. Deactivated {inactive_count} legacy templates."
            )
        )