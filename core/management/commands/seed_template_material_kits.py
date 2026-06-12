from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ServiceTemplate, MaterialCatalog, ServiceTemplateMaterial


D = Decimal


KITS = [
    {
        "template": "Appliance Connections",
        "materials": [
            ("Dishwasher Cord Kit", D("1")),
            ("Garbage Disposal Switch Kit", D("1")),
            ("15A Tamper Resistant Receptacle", D("1")),
            ("1-Gang Plastic Nail-On Box", D("1")),
            ("1-Gang Decora Plate", D("1")),
            ("Blue Wire Nuts", D("4")),
        ],
    },
    {
        "template": "Ceiling Fans & Ventilation",
        "materials": [
            ("Ceiling Fan", D("1")),
            ("Ceiling Fan Rated Box", D("1")),
            ("Adjustable Fan Brace Box", D("1")),
            ("Single Pole Switch", D("1")),
            ("1-Gang Toggle Plate", D("1")),
            ("Blue Wire Nuts", D("4")),
        ],
    },
    {
        "template": "Dedicated Circuits",
        "materials": [
            ("12/2 NM-B Cable", D("75")),
            ("Square D Homeline 20A Single Pole Breaker", D("1")),
            ("20A Tamper Resistant Receptacle", D("1")),
            ("1-Gang Plastic Nail-On Box", D("1")),
            ("1-Gang Decora Plate", D("1")),
            ("Yellow Wire Nuts", D("4")),
            ("NM Cable Staples", D("15")),
        ],
    },
    {
        "template": "EV Charger Installation",
        "materials": [
            ("Tesla Wall Connector", D("1")),
            ("Square D Homeline 60A Two Pole Breaker", D("1")),
            ("#6 THHN Copper Black", D("120")),
            ("#6 THHN Copper White", D("60")),
            ("#10 THHN Copper Green", D("60")),
            ("3/4 PVC Conduit Schedule 40", D("6")),
            ("3/4 PVC Male Adapter", D("2")),
            ("3/4 PVC LB", D("1")),
            ("3/4 PVC Coupling", D("2")),
            ("Zip Ties", D("10")),
        ],
    },
    {
        "template": "Exterior Electrical",
        "materials": [
            ("Exterior Bell Box", D("1")),
            ("Weather Resistant GFCI Receptacle", D("1")),
            ("Weatherproof While-In-Use Extra Duty Cover", D("1")),
            ("12/2 NM-B Cable", D("40")),
            ("1/2 PVC Conduit Schedule 40", D("2")),
            ("1/2 PVC Male Adapter", D("2")),
            ("Yellow Wire Nuts", D("4")),
        ],
    },
    {
        "template": "Generator & Backup Power",
        "materials": [
            ("Generator Inlet 50A", D("1")),
            ("Generator Power Cord 50A", D("1")),
            ("Square D Homeline Generator Interlock Kit 150-225A Indoor", D("1")),
            ("Square D Homeline 50A Two Pole Breaker", D("1")),
            ("#6 THHN Copper Black", D("80")),
            ("#6 THHN Copper White", D("40")),
            ("#10 THHN Copper Green", D("40")),
            ("1 Inch PVC Conduit Schedule 40", D("4")),
            ("1 Inch PVC LB", D("1")),
        ],
    },
    {
        "template": "Grounding & Bonding",
        "materials": [
            ("8 ft Ground Rod", D("2")),
            ("Ground Rod Clamp", D("2")),
            ("#6 Bare Copper Ground Wire", D("50")),
            ("Water Pipe Ground Clamp", D("1")),
            ("Intersystem Bonding Bridge", D("1")),
            ("Bonding Bushing 1 Inch", D("1")),
        ],
    },
    {
        "template": "Landscape & Specialty Lighting",
        "materials": [
            ("Landscape Transformer", D("1")),
            ("Landscape Stake Light", D("4")),
            ("14/2 Landscape Lighting Cable", D("100")),
            ("Photocell", D("1")),
            ("Exterior Bell Box", D("1")),
            ("Weatherproof In-Use Cover", D("1")),
        ],
    },
    {
        "template": "Lighting Installation & Repair",
        "materials": [
            ("Ceiling Light Fixture", D("1")),
            ("Single Pole Switch", D("1")),
            ("1-Gang Toggle Plate", D("1")),
            ("14/2 NM-B Cable", D("40")),
            ("Blue Wire Nuts", D("6")),
            ("NM Cable Staples", D("10")),
        ],
    },
    {
        "template": "Low Voltage & Communications",
        "materials": [
            ("Cat6 Cable", D("100")),
            ("Keystone Jack Cat6", D("2")),
            ("Data Wall Plate", D("2")),
            ("Coax Cable RG6", D("50")),
        ],
    },
    {
        "template": "Panel & Service Upgrades",
        "materials": [
            ("Square D Homeline 200A Indoor Main Breaker Panel 40/80", D("1")),
            ("200A Meter Socket Ringless", D("1")),
            ("Square D Homeline Whole Home Surge Protector", D("1")),
            ("8 ft Ground Rod", D("2")),
            ("Ground Rod Clamp", D("2")),
            ("Intersystem Bonding Bridge", D("1")),
            ("#6 Bare Copper Ground Wire", D("40")),
            ("Water Pipe Ground Clamp", D("1")),
            ("Square D Homeline Ground Bar Kit", D("1")),
            ("Square D Homeline Filler Plates", D("4")),
        ],
    },
    {
        "template": "Pools, Spas & Outdoor Equipment",
        "materials": [
            ("60A Spa Panel", D("1")),
            ("Spa Disconnect GFCI", D("1")),
            ("Pool Timer", D("1")),
            ("Pool Disconnect", D("1")),
            ("Equipotential Bonding Clamp", D("4")),
            ("#8 THHN Copper Green", D("100")),
            ("1 Inch PVC Conduit Schedule 40", D("4")),
            ("1 Inch PVC LB", D("1")),
        ],
    },
    {
        "template": "Receptacles & Power Devices",
        "materials": [
            ("20A Tamper Resistant Receptacle", D("1")),
            ("1-Gang Plastic Nail-On Box", D("1")),
            ("1-Gang Decora Plate", D("1")),
            ("12/2 NM-B Cable", D("25")),
            ("Yellow Wire Nuts", D("4")),
            ("NM Cable Staples", D("8")),
        ],
    },
    {
        "template": "Recessed Lighting",
        "materials": [
            ("6 Inch LED Recessed Wafer Light", D("6")),
            ("14/2 NM-B Cable", D("100")),
            ("Single Pole Switch", D("1")),
            ("1-Gang Toggle Plate", D("1")),
            ("Blue Wire Nuts", D("12")),
            ("NM Cable Staples", D("20")),
        ],
    },
    {
        "template": "Remodels & Additions",
        "materials": [
            ("12/2 NM-B Cable", D("150")),
            ("14/2 NM-B Cable", D("150")),
            ("20A Tamper Resistant Receptacle", D("6")),
            ("15A Tamper Resistant Receptacle", D("6")),
            ("Single Pole Switch", D("4")),
            ("1-Gang Plastic Nail-On Box", D("10")),
            ("2-Gang Plastic Nail-On Box", D("4")),
            ("1-Gang Decora Plate", D("10")),
            ("2-Gang Decora Plate", D("4")),
            ("Yellow Wire Nuts", D("20")),
            ("Blue Wire Nuts", D("20")),
            ("NM Cable Staples", D("50")),
        ],
    },
    {
        "template": "Smart Home Electrical",
        "materials": [
            ("Leviton Smart Switch", D("2")),
            ("Lutron Caseta Dimmer", D("1")),
            ("Lutron Caseta Pico Remote", D("1")),
            ("Lutron Smart Bridge", D("1")),
            ("Ring Doorbell", D("1")),
            ("Nest Thermostat", D("1")),
        ],
    },
    {
        "template": "Smoke & Life Safety",
        "materials": [
            ("Smoke Detector Hardwired", D("2")),
            ("Smoke/CO Detector Hardwired", D("1")),
            ("14/3 NM-B Cable", D("60")),
            ("Smoke Detector Remodel Box", D("3")),
            ("Blue Wire Nuts", D("8")),
        ],
    },
    {
        "template": "Surge Protection",
        "materials": [
            ("Square D Homeline Whole Home Surge Protector", D("1")),
            ("Square D Homeline 20A Two Pole Breaker", D("1")),
            ("#12 THHN Copper Black", D("8")),
            ("#12 THHN Copper White", D("4")),
            ("#12 THHN Copper Green", D("4")),
        ],
    },
    {
        "template": "Switches & Controls",
        "materials": [
            ("Single Pole Switch", D("1")),
            ("3-Way Switch", D("1")),
            ("Dimmer Switch", D("1")),
            ("Timer Switch", D("1")),
            ("1-Gang Plastic Nail-On Box", D("1")),
            ("1-Gang Toggle Plate", D("1")),
            ("Blue Wire Nuts", D("4")),
        ],
    },
    {
        "template": "Wiring Repairs & Rewiring",
        "materials": [
            ("12/2 NM-B Cable", D("75")),
            ("14/2 NM-B Cable", D("75")),
            ("Blue Wire Nuts", D("12")),
            ("Yellow Wire Nuts", D("12")),
            ("Wago 2-Port Lever Connector", D("10")),
            ("Wago 3-Port Lever Connector", D("10")),
            ("NM Cable Staples", D("20")),
            ("4 Inch Square Metal Box", D("1")),
        ],
    },
]


INTENTIONALLY_MANUAL = [
    "Code Corrections",
    "Custom Electrical Work",
    "Diagnostic & Troubleshooting",
    "Home Electrical Inspections",
    "Permit & Utility Coordination",
]


class Command(BaseCommand):
    help = "Seed ServiceTemplateMaterial kits for JCV master service templates."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--clear-existing", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        clear_existing = options["clear_existing"]

        templates = list(ServiceTemplate.objects.filter(active=True).order_by("name"))
        material_map = {m.name: m for m in MaterialCatalog.objects.filter(active=True)}
        kit_map = {kit["template"]: kit for kit in KITS}

        created = 0
        updated = 0
        skipped_manual = 0
        skipped_no_kit = 0
        skipped_missing_materials = []

        self.stdout.write(self.style.WARNING("Seeding JCV template material kits..."))
        self.stdout.write(f"Active templates found: {len(templates)}")
        self.stdout.write(f"Active materials found: {len(material_map)}")
        self.stdout.write(f"Kits defined: {len(KITS)}")

        with transaction.atomic():
            if clear_existing:
                count = ServiceTemplateMaterial.objects.count()
                self.stdout.write(self.style.WARNING(f"Clearing existing template materials: {count}"))
                if not dry_run:
                    ServiceTemplateMaterial.objects.all().delete()

            for template in templates:
                if template.name in INTENTIONALLY_MANUAL:
                    skipped_manual += 1
                    self.stdout.write(self.style.WARNING(f"Manual template skipped: {template.name}"))
                    continue

                kit = kit_map.get(template.name)

                if not kit:
                    skipped_no_kit += 1
                    self.stdout.write(self.style.ERROR(f"No kit defined for: {template.name}"))
                    continue

                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS(f"Template: {template.name}"))

                for material_name, quantity in kit["materials"]:
                    material = material_map.get(material_name)

                    if not material:
                        skipped_missing_materials.append((template.name, material_name))
                        self.stdout.write(self.style.ERROR(f"  Missing material: {material_name}"))
                        continue

                    self.stdout.write(f"  {material_name} x {quantity}")

                    if dry_run:
                        continue

                    obj, was_created = ServiceTemplateMaterial.objects.update_or_create(
                        service_template=template,
                        material=material,
                        defaults={"quantity": quantity},
                    )

                    if was_created:
                        created += 1
                    else:
                        updated += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Template material kit seeding complete."))
        self.stdout.write(f"Rows created: {created}")
        self.stdout.write(f"Rows updated: {updated}")
        self.stdout.write(f"Manual templates skipped: {skipped_manual}")
        self.stdout.write(f"Templates without kit: {skipped_no_kit}")
        self.stdout.write(f"Missing materials: {len(skipped_missing_materials)}")

        if skipped_missing_materials:
            self.stdout.write(self.style.ERROR(""))
            self.stdout.write(self.style.ERROR("Missing material details:"))
            for template_name, material_name in skipped_missing_materials:
                self.stdout.write(self.style.ERROR(f"{template_name}: {material_name}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No database changes saved."))