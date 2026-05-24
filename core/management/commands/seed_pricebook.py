from django.core.management.base import BaseCommand
from core.models import ServiceTemplate


LABOR_RATE = 110
MATERIAL_MARKUP = 1.35


PRICEBOOK = [
    # Dedicated Circuits
    ("🔌", "15A Dedicated Circuit", "Dedicated Circuits", 3.0, 95, 435),
    ("🔌", "20A Dedicated Circuit", "Dedicated Circuits", 3.0, 115, 485),
    ("🔌", "30A Dedicated Circuit", "Dedicated Circuits", 3.5, 175, 625),
    ("🔌", "40A Dedicated Circuit", "Dedicated Circuits", 4.0, 225, 745),
    ("🔌", "50A Dedicated Circuit", "Dedicated Circuits", 4.0, 275, 825),
    ("🔌", "EV Charger Circuit", "Dedicated Circuits", 5.0, 375, 1050),
    ("🔌", "Interlock Kit Install", "Generator / Backup Power", 3.0, 250, 695),
    ("🔌", "Manual Transfer Switch Install", "Generator / Backup Power", 5.0, 450, 1195),
    ("🔌", "Portable Generator Inlet Install", "Generator / Backup Power", 4.0, 325, 895),
    ("🔌", "RV Outlet Install", "Dedicated Circuits", 4.0, 250, 795),
    ("🔌", "Standby Generator Electrical Hookup", "Generator / Backup Power", 8.0, 850, 1895),

    # Fans
    ("🌀", "Attic Fan Install", "Fans", 3.0, 175, 525),
    ("🌀", "Bathroom Exhaust Fan New Install", "Fans", 3.0, 125, 475),
    ("🌀", "Bathroom Exhaust Fan Replacement", "Fans", 2.0, 80, 325),
    ("🌀", "Ceiling Fan Install - Existing Fan Box", "Fans", 1.5, 40, 225),
    ("🌀", "Ceiling Fan Install - New Fan Box", "Fans", 3.0, 95, 425),
    ("🌀", "Ceiling Fan Replacement", "Fans", 1.5, 35, 195),

    # Lighting
    ("💡", "Attic Light Install", "Lighting", 2.0, 60, 295),
    ("💡", "Chandelier Install", "Lighting", 2.5, 45, 375),
    ("💡", "Exterior Flood Light Install", "Lighting", 2.0, 85, 325),
    ("💡", "Garage Lighting Install", "Lighting", 2.5, 125, 475),
    ("💡", "LED Strip Lighting Install", "Lighting", 3.0, 175, 595),
    ("💡", "Landscape Lighting Transformer Install", "Lighting", 2.0, 125, 395),
    ("💡", "Light Fixture Replacement", "Lighting", 1.0, 25, 165),
    ("💡", "Motion Light Install", "Lighting", 2.0, 80, 325),
    ("💡", "Pendant Light Install", "Lighting", 1.5, 30, 225),
    ("💡", "Recessed Lighting Install", "Lighting", 2.0, 75, 325),
    ("💡", "Security Light Install", "Lighting", 2.0, 95, 345),
    ("💡", "Shop Lighting Install", "Lighting", 3.0, 175, 625),
    ("💡", "Under Cabinet Lighting Install", "Lighting", 3.0, 175, 625),
    ("💡", "Vanity Light Install", "Lighting", 1.5, 35, 225),

    # Low Voltage
    ("📡", "Camera Power Install", "Low Voltage", 1.5, 45, 225),
    ("📡", "Doorbell Transformer Replacement", "Low Voltage", 1.0, 35, 165),
    ("📡", "Ethernet Drop Install", "Low Voltage", 2.0, 65, 275),
    ("📡", "Low Voltage Wire Repair", "Low Voltage", 1.5, 35, 225),
    ("📡", "Smart Doorbell Install", "Low Voltage", 1.0, 25, 150),
    ("📡", "TV Outlet / Low Voltage Brush Plate", "Low Voltage", 1.5, 45, 225),
    ("📡", "Wi-Fi Access Point Outlet Install", "Low Voltage", 2.0, 65, 295),

    # Outlets / Switches
    ("🔘", "Add New Outlet - Existing Circuit", "Outlets / Switches", 1.5, 45, 245),
    ("🔘", "Dimmer Switch Install", "Outlets / Switches", 1.0, 35, 165),
    ("🔘", "Four Way Switch Replacement", "Outlets / Switches", 1.25, 25, 195),
    ("🔘", "GFCI Outlet Replacement", "Outlets / Switches", 1.0, 30, 175),
    ("🔘", "Garage GFCI Outlet Install", "Outlets / Switches", 1.5, 45, 245),
    ("🔘", "Light Switch Replacement", "Outlets / Switches", 1.0, 15, 145),
    ("🔘", "Motion Sensor Switch Install", "Outlets / Switches", 1.0, 40, 175),
    ("🔘", "Outdoor GFCI Outlet Install", "Outlets / Switches", 1.5, 65, 275),
    ("🔘", "Quad Outlet Install", "Outlets / Switches", 1.5, 45, 245),
    ("🔘", "Smart Outlet Install", "Outlets / Switches", 1.0, 35, 165),
    ("🔘", "Smart Switch Install", "Outlets / Switches", 1.0, 40, 175),
    ("🔘", "Standard Outlet Replacement", "Outlets / Switches", 1.0, 15, 145),
    ("🔘", "Tamper Resistant Outlet Replacement", "Outlets / Switches", 1.0, 18, 150),
    ("🔘", "Three Way Switch Replacement", "Outlets / Switches", 1.25, 25, 195),
    ("🔘", "Timer Switch Install", "Outlets / Switches", 1.0, 40, 175),
    ("🔘", "USB Outlet Install", "Outlets / Switches", 1.0, 35, 165),
    ("🔘", "Weatherproof Outlet Install", "Outlets / Switches", 1.5, 65, 275),

    # Panel / Service Work
    ("⚡", "100A Panel Install - Indoor", "Panel & Service Work", 8.0, 650, 1895),
    ("⚡", "100A Panel Install - Outdoor", "Panel & Service Work", 9.0, 750, 2195),
    ("⚡", "150A Panel Install - Indoor", "Panel & Service Work", 9.0, 800, 2495),
    ("⚡", "150A Panel Install - Outdoor", "Panel & Service Work", 10.0, 900, 2795),
    ("⚡", "200A Panel Install - Indoor", "Panel & Service Work", 10.0, 950, 2995),
    ("⚡", "200A Panel Install - Outdoor", "Panel & Service Work", 11.0, 1100, 3495),
    ("⚡", "Breaker Replacement", "Panel & Service Work", 1.0, 45, 185),
    ("⚡", "Grounding Electrode System Upgrade", "Panel & Service Work", 3.0, 175, 625),
    ("⚡", "Meter/Main Combo Replacement", "Panel & Service Work", 10.0, 1200, 3695),
    ("⚡", "Overhead Service Upgrade", "Panel & Service Work", 12.0, 1450, 4495),
    ("⚡", "Panel Tune-Up / Breaker Cleanup", "Panel & Service Work", 2.0, 50, 325),
    ("⚡", "Underground Service Upgrade", "Panel & Service Work", 14.0, 1750, 5495),
    ("⚡", "Whole Home Surge Protector Install", "Panel & Service Work", 1.5, 175, 395),

    # Panel Upgrades branded
    ("⚡", "Panel Changeout - 100A Square D Homeline", "Panel & Service Work", 8.0, 650, 1895),
    ("⚡", "Panel Upgrade - 200A Square D Homeline Indoor", "Panel & Service Work", 10.0, 950, 2995),
    ("⚡", "Panel Upgrade - 200A Square D Homeline Outdoor", "Panel & Service Work", 11.0, 1100, 3495),
    ("⚡", "Subpanel Install - 100A Square D Homeline", "Subpanels", 6.0, 650, 1895),

    # Subpanels
    ("🧰", "100A Subpanel Install - Indoor", "Subpanels", 6.0, 575, 1695),
    ("🧰", "100A Subpanel Install - Outdoor", "Subpanels", 7.0, 700, 2095),
    ("🧰", "125A Subpanel Install - Indoor", "Subpanels", 7.0, 700, 2195),
    ("🧰", "125A Subpanel Install - Outdoor", "Subpanels", 8.0, 825, 2495),
    ("🧰", "60A Subpanel Install - Indoor", "Subpanels", 5.0, 425, 1295),
    ("🧰", "60A Subpanel Install - Outdoor", "Subpanels", 6.0, 550, 1695),

    # Troubleshooting
    ("🔎", "Troubleshooting Level 1 - Basic Diagnostic", "Troubleshooting", 1.0, 0, 125),
    ("🔎", "Troubleshooting Level 2 - Intermediate Diagnostic", "Troubleshooting", 2.5, 25, 325),
    ("🔎", "Troubleshooting Level 3 - Advanced Diagnostic", "Troubleshooting", 4.0, 50, 550),

    # New Important Add-Ons
    ("🧾", "Permit / Inspection Fee", "Add-Ons", 0.0, 0, 250),
    ("🚚", "Trip Charge", "Add-Ons", 0.5, 0, 85),
    ("🌙", "After-Hours Emergency Service Call", "Add-Ons", 1.0, 0, 225),
    ("⛏️", "Small Trenching Add-On", "Add-Ons", 3.0, 75, 495),
    ("🧰", "Panel Labeling / Circuit Mapping", "Panel & Service Work", 2.0, 15, 295),
    ("⚡", "Main Breaker Replacement", "Panel & Service Work", 2.0, 175, 495),
    ("⚡", "AFCI / GFCI Breaker Install", "Panel & Service Work", 1.0, 75, 225),
    ("🔥", "Smoke / CO Detector Replacement", "Safety Devices", 1.0, 45, 165),
    ("🔥", "Smoke / CO Detector New Install", "Safety Devices", 2.0, 85, 325),
    ("🔌", "Dishwasher / Disposal Circuit", "Dedicated Circuits", 3.0, 115, 485),
    ("🔌", "Microwave Circuit", "Dedicated Circuits", 3.0, 115, 485),
    ("🔌", "Dryer Circuit", "Dedicated Circuits", 4.0, 225, 745),
    ("🔌", "Range Circuit", "Dedicated Circuits", 4.0, 275, 825),
    ("🔌", "Mini-Split Circuit", "Dedicated Circuits", 4.0, 225, 745),
    ("💧", "Hot Tub / Spa Circuit", "Dedicated Circuits", 6.0, 475, 1395),
    ("🏊", "Pool Equipment Bonding Repair", "Pool / Outdoor Electrical", 3.0, 175, 625),
    ("🏠", "Home Inspection Electrical Repair Package", "Troubleshooting", 4.0, 150, 695),
    ("🏢", "Commercial Dedicated Circuit", "Commercial", 4.0, 225, 825),
    ("🏢", "Commercial Lighting Repair", "Commercial", 2.0, 85, 345),
    ("🏢", "Exit Sign / Emergency Light Install", "Commercial", 2.0, 125, 425),
    ("🏢", "Disconnect Install", "Commercial", 3.0, 225, 695),
]


class Command(BaseCommand):
    help = "Seed or update JCV Power Solutions service template price book."

    def handle(self, *args, **options):
        template_fields = {field.name for field in ServiceTemplate._meta.fields}
        created_count = 0
        updated_count = 0

        for icon, name, category, labor_hours, material_cost, sell_price in PRICEBOOK:
            defaults = {}

            if "icon" in template_fields:
                defaults["icon"] = icon
            if "category" in template_fields:
                defaults["category"] = category
            if "default_labor_hours" in template_fields:
                defaults["default_labor_hours"] = labor_hours
            if "default_price" in template_fields:
                defaults["default_price"] = sell_price
            if "active" in template_fields:
                defaults["active"] = True

            # Optional newer fields, if you add them later.
            if "labor_rate" in template_fields:
                defaults["labor_rate"] = LABOR_RATE
            if "estimated_material_cost" in template_fields:
                defaults["estimated_material_cost"] = material_cost
            if "material_markup" in template_fields:
                defaults["material_markup"] = MATERIAL_MARKUP
            if "estimated_material_sell_price" in template_fields:
                defaults["estimated_material_sell_price"] = round(material_cost * MATERIAL_MARKUP, 2)

            obj, created = ServiceTemplate.objects.update_or_create(
                name=name,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Price book seeded. Created: {created_count}. Updated: {updated_count}."
            )
        )