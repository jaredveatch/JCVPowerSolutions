from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import (
    MaterialCatalog,
    ServiceTemplate,
    ServiceTemplateMaterial,
)


class Command(BaseCommand):
    help = "Seed residential panel upgrade service templates."

    def get_material(self, name, manufacturer="Generic", part_number="", unit="each", labor_hours="0.00"):
        material, created = MaterialCatalog.objects.get_or_create(
            name=name,
            defaults={
                "manufacturer": manufacturer,
                "part_number": part_number,
                "unit": unit,
                "unit_cost": Decimal("0.00"),
                "labor_hours": Decimal(labor_hours),
                "active": True,
            },
        )
        return material

    def add_material(self, template, name, qty):
        material = self.get_material(name)

        ServiceTemplateMaterial.objects.update_or_create(
            service_template=template,
            material=material,
            defaults={
                "quantity": Decimal(str(qty)),
            },
        )

    def handle(self, *args, **kwargs):

        panel_templates = [
            {
                "name": "Panel Upgrade - 200A Square D Homeline Outdoor",
                "description": "Replace/upgrade exterior residential panel with 200A Square D Homeline outdoor load center.",
                "materials": [
                    ("Square D Homeline 200A Outdoor Main Breaker Panel 40/80", 1),
                    ("Square D Homeline 20A Single Pole Breaker", 10),
                    ("Square D Homeline 15A Single Pole Breaker", 6),
                    ("Square D Homeline 30A Two Pole Breaker", 1),
                    ("Square D Homeline 40A Two Pole Breaker", 1),
                    ("Square D Homeline 50A Two Pole Breaker", 1),
                    ("Square D Homeline Whole Home Surge Protector", 1),
                    ("Square D Homeline Ground Bar Kit", 1),
                    ("Square D Homeline Filler Plates", 6),

                    ("Service Entrance Cable 4/0 Aluminum SER", 20),
                    ("4/0 Aluminum XHHW Conductor", 60),
                    ("#6 Bare Copper Ground Wire", 30),
                    ("8 ft Ground Rod", 2),
                    ("Ground Rod Clamp", 2),
                    ("Intersystem Bonding Bridge", 1),
                    ("Water Pipe Ground Clamp", 1),

                    ("2 Inch PVC Conduit Schedule 40", 10),
                    ("2 Inch Weatherhead", 1),
                    ("2 Inch Rigid Locknut", 2),
                    ("2 Inch Rigid Bushing", 2),
                    ("Bonding Bushing 2 Inch", 1),
                    ("Anti-Ox Compound", 1),
                    ("Duct Seal", 1),
                    ("Electrical Tape", 1),
                ],
            },
            {
                "name": "Panel Upgrade - 200A Square D Homeline Indoor",
                "description": "Replace/upgrade interior residential panel with 200A Square D Homeline indoor load center.",
                "materials": [
                    ("Square D Homeline 200A Indoor Main Breaker Panel 40/80", 1),
                    ("Square D Homeline 20A Single Pole Breaker", 10),
                    ("Square D Homeline 15A Single Pole Breaker", 6),
                    ("Square D Homeline 30A Two Pole Breaker", 1),
                    ("Square D Homeline 40A Two Pole Breaker", 1),
                    ("Square D Homeline 50A Two Pole Breaker", 1),
                    ("Square D Homeline Whole Home Surge Protector", 1),
                    ("Square D Homeline Ground Bar Kit", 1),
                    ("Square D Homeline Filler Plates", 6),

                    ("Service Entrance Cable 4/0 Aluminum SER", 20),
                    ("#6 Bare Copper Ground Wire", 30),
                    ("8 ft Ground Rod", 2),
                    ("Ground Rod Clamp", 2),
                    ("Intersystem Bonding Bridge", 1),
                    ("Water Pipe Ground Clamp", 1),

                    ("Bonding Bushing 2 Inch", 1),
                    ("Anti-Ox Compound", 1),
                    ("Duct Seal", 1),
                    ("Electrical Tape", 1),
                ],
            },
            {
                "name": "Panel Changeout - 100A Square D Homeline",
                "description": "Basic residential 100A panel replacement using Square D Homeline equipment.",
                "materials": [
                    ("Square D Homeline 100A Indoor Main Breaker Panel 20/40", 1),
                    ("Square D Homeline 20A Single Pole Breaker", 8),
                    ("Square D Homeline 15A Single Pole Breaker", 6),
                    ("Square D Homeline 30A Two Pole Breaker", 1),
                    ("Square D Homeline Whole Home Surge Protector", 1),
                    ("Square D Homeline Ground Bar Kit", 1),
                    ("Square D Homeline Filler Plates", 4),

                    ("Service Entrance Cable #2 Aluminum SER", 20),
                    ("#6 Bare Copper Ground Wire", 30),
                    ("8 ft Ground Rod", 2),
                    ("Ground Rod Clamp", 2),
                    ("Intersystem Bonding Bridge", 1),
                    ("Anti-Ox Compound", 1),
                    ("Electrical Tape", 1),
                ],
            },
            {
                "name": "Subpanel Install - 100A Square D Homeline",
                "description": "Install 100A residential subpanel with feeder and grounding materials.",
                "materials": [
                    ("Square D Homeline 100A Main Lug Subpanel 6/12 Indoor", 1),
                    ("Square D Homeline 100A Two Pole Breaker", 1),
                    ("Square D Homeline 20A Single Pole Breaker", 4),
                    ("Square D Homeline 15A Single Pole Breaker", 4),
                    ("Square D Homeline Ground Bar Kit", 1),
                    ("Square D Homeline Filler Plates", 4),

                    ("Service Entrance Cable #2 Aluminum SER", 50),
                    ("Anti-Ox Compound", 1),
                    ("Electrical Tape", 1),
                ],
            },
        ]

        for item in panel_templates:
            template, created = ServiceTemplate.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": "Panel Upgrades",
                    "customer_description": item["description"],
                    "internal_checklist": "Verify existing service, grounding, bonding, panel location, utility requirements, permits, and load calculation before final install.",
                    "default_labor_hours": Decimal("8.00"),
                    "default_price": Decimal("0.00"),
                    "active": True,
                    "icon": "⚡",
                },
            )

            for material_name, qty in item["materials"]:
                self.add_material(template, material_name, qty)

        self.stdout.write(
            self.style.SUCCESS("Panel upgrade templates seeded successfully.")
        )