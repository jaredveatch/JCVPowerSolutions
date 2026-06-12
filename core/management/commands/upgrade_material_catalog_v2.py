from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import MaterialCatalog


MATERIALS_TO_REMOVE = [
    "50A EV Circuit Material Allowance",
    "60A EV Hardwire Circuit Material Allowance",
    "Microwave Dedicated Circuit Material",
]


MATERIALS_TO_ADD = [
    # =====================================================
    # SQUARE D HOMELINE PANELS / LOAD CENTERS
    # =====================================================
    ("Panels", "Square D Homeline 125A Indoor Main Breaker Panel 30/60", "Square D", "HOM3060M125PC", "each", "0.00", "3.00"),
    ("Panels", "Square D Homeline 150A Indoor Main Breaker Panel 40/80", "Square D", "HOM4080M150PC", "each", "0.00", "3.50"),
    ("Panels", "Square D Homeline 225A Indoor Main Breaker Panel 54/108", "Square D", "HOM54108M225PC", "each", "0.00", "4.25"),

    ("Panels", "Square D Homeline 125A Outdoor Main Breaker Panel 30/60", "Square D", "HOM3060M125PRB", "each", "0.00", "3.50"),
    ("Panels", "Square D Homeline 150A Outdoor Main Breaker Panel 40/80", "Square D", "HOM4080M150PRB", "each", "0.00", "3.75"),
    ("Panels", "Square D Homeline 200A Outdoor Main Breaker Panel 42/84", "Square D", "HOM4284M200PRB", "each", "0.00", "4.25"),
    ("Panels", "Square D Homeline 225A Outdoor Main Breaker Panel 42/84", "Square D", "HOM4284M225PRB", "each", "0.00", "4.50"),

    ("Panels", "Square D Homeline 70A Main Lug Subpanel 4/8 Indoor", "Square D", "HOM48L70SCP", "each", "0.00", "1.25"),
    ("Panels", "Square D Homeline 100A Main Lug Subpanel 12/24 Indoor", "Square D", "HOM1224L100PC", "each", "0.00", "1.75"),
    ("Panels", "Square D Homeline 200A Main Lug Subpanel 40/80 Indoor", "Square D", "HOM4080L225PC", "each", "0.00", "3.00"),
    ("Panels", "Square D Homeline 200A Main Lug Subpanel 42/84 Indoor", "Square D", "HOM4284L225PC", "each", "0.00", "3.25"),

    ("Panels", "Square D Homeline Generator Ready Panel 100A", "Square D", "Generator Ready 100A", "each", "0.00", "4.00"),
    ("Panels", "Square D Homeline Generator Ready Panel 200A", "Square D", "Generator Ready 200A", "each", "0.00", "5.00"),

    ("Panels", "Square D Homeline 100A Mobile Home Outdoor Feed Through", "Square D", "Mobile Home 100A Feed Through", "each", "0.00", "3.00"),
    ("Panels", "Square D Homeline 125A Mobile Home Outdoor Feed Through", "Square D", "Mobile Home 125A Feed Through", "each", "0.00", "3.50"),

    # =====================================================
    # MAIN BREAKERS
    # =====================================================
    ("Breakers", "Square D Homeline 100A Main Breaker", "Square D", "HOM2100MB", "each", "0.00", "0.50"),
    ("Breakers", "Square D Homeline 125A Main Breaker", "Square D", "HOM2125MB", "each", "0.00", "0.50"),
    ("Breakers", "Square D Homeline 150A Main Breaker", "Square D", "HOM2150MB", "each", "0.00", "0.60"),
    ("Breakers", "Square D Homeline 200A Main Breaker", "Square D", "HOM2200MB", "each", "0.00", "0.75"),
    ("Breakers", "Square D Homeline 225A Main Breaker", "Square D", "HOM2225MB", "each", "0.00", "0.75"),

    # =====================================================
    # LOW VOLTAGE / LANDSCAPE
    # =====================================================
    ("Low Voltage", "18/2 Thermostat Wire", "Southwire", "18/2 Thermostat", "ft", "0.00", "0.01"),
    ("Low Voltage", "18/5 Thermostat Wire", "Southwire", "18/5 Thermostat", "ft", "0.00", "0.01"),
    ("Low Voltage", "16/2 Landscape Lighting Cable", "Southwire", "16/2 LV Landscape", "ft", "0.00", "0.02"),
    ("Low Voltage", "14/2 Landscape Lighting Cable", "Southwire", "14/2 LV Landscape", "ft", "0.00", "0.025"),

    # =====================================================
    # BOXES / WIRING PROTECTION
    # =====================================================
    ("Boxes", "Old Work 4-Gang Box", "Carlon", "4G Old Work", "each", "0.00", "0.35"),
    ("Boxes", "4-Gang Mud Ring", "Raco", "4G Mud Ring", "each", "0.00", "0.15"),
    ("Boxes", "4 Inch Octagon Box", "Raco", "4 Octagon", "each", "0.00", "0.15"),
    ("Boxes", "Metal Switch Box", "Raco", "Metal Switch Box", "each", "0.00", "0.15"),
    ("Boxes", "Romex Connector", "Halex", "NM Connector", "each", "0.00", "0.03"),
    ("Boxes", "MC Cable Connector", "Halex", "MC Connector", "each", "0.00", "0.04"),
    ("Boxes", "1/2 Inch Snap-In Bushing", "Arlington", "Snap-In Bushing", "each", "0.00", "0.01"),
    ("Boxes", "Protective Nail Plate", "Simpson", "Nail Plate", "each", "0.00", "0.02"),

    # =====================================================
    # EXTERIOR
    # =====================================================
    ("Exterior", "FS Box Single Gang", "Bell", "1G FS Box", "each", "0.00", "0.20"),
    ("Exterior", "FS Box Double Gang", "Bell", "2G FS Box", "each", "0.00", "0.25"),
    ("Exterior", "Exterior Bell Box", "Bell", "Weatherproof Box", "each", "0.00", "0.20"),
    ("Exterior", "Photocell", "Intermatic", "Photocell", "each", "0.00", "0.25"),
    ("Exterior", "Post Light Fixture", "Generic", "Post Light", "each", "0.00", "0.75"),
    ("Exterior", "Landscape Stake Light", "Generic", "Landscape Stake Light", "each", "0.00", "0.25"),

    # =====================================================
    # POOL / SPA
    # =====================================================
    ("Pools & Spas", "50A Spa Panel", "Square D", "50A Spa Panel", "each", "0.00", "1.00"),
    ("Pools & Spas", "60A Spa Panel", "Square D", "60A Spa Panel", "each", "0.00", "1.00"),
    ("Pools & Spas", "Spa Disconnect GFCI", "Square D", "Spa Disconnect GFCI", "each", "0.00", "1.00"),
    ("Pools & Spas", "Pool Timer", "Intermatic", "Pool Timer", "each", "0.00", "0.75"),
    ("Pools & Spas", "Pool Disconnect", "Square D", "Pool Disconnect", "each", "0.00", "0.75"),
    ("Pools & Spas", "Equipotential Bonding Clamp", "Erico", "Pool Bond Clamp", "each", "0.00", "0.10"),

    # =====================================================
    # EV
    # =====================================================
    ("EV Charging", "Tesla Wall Connector", "Tesla", "Wall Connector", "each", "0.00", "1.00"),
    ("EV Charging", "ChargePoint Home Flex", "ChargePoint", "Home Flex", "each", "0.00", "1.00"),
    ("EV Charging", "Emporia EV Charger", "Emporia", "EV Charger", "each", "0.00", "1.00"),
    ("EV Charging", "EV Pedestal Mount", "Generic", "EV Pedestal", "each", "0.00", "1.50"),
    ("EV Charging", "Load Management Device", "Generic", "EV Load Manager", "each", "0.00", "1.50"),

    # =====================================================
    # MINI SPLITS / HVAC
    # =====================================================
    ("HVAC", "Mini Split Disconnect", "Square D", "Mini Split Disconnect", "each", "0.00", "0.50"),
    ("HVAC", "Mini Split Surge Protector", "Intermatic", "Mini Split SPD", "each", "0.00", "0.35"),
    ("HVAC", "Mini Split Whip", "Southwire", "Mini Split Whip", "each", "0.00", "0.25"),

    # =====================================================
    # SMART HOME
    # =====================================================
    ("Smart Home", "Nest Thermostat", "Google Nest", "Nest Thermostat", "each", "0.00", "0.50"),
    ("Smart Home", "Ecobee Thermostat", "Ecobee", "Ecobee Thermostat", "each", "0.00", "0.50"),
    ("Smart Home", "Lutron Caseta Dimmer", "Lutron", "Caseta Dimmer", "each", "0.00", "0.35"),
    ("Smart Home", "Lutron Caseta Pico Remote", "Lutron", "Pico Remote", "each", "0.00", "0.15"),
    ("Smart Home", "Lutron Smart Bridge", "Lutron", "Smart Bridge", "each", "0.00", "0.25"),
    ("Smart Home", "Leviton Smart Switch", "Leviton", "Smart Switch", "each", "0.00", "0.35"),
    ("Smart Home", "Ring Doorbell", "Ring", "Video Doorbell", "each", "0.00", "0.50"),

    # =====================================================
    # SURGE PROTECTION
    # =====================================================
    ("Surge Protection", "Type 2 SPD 80kA", "Generic", "Type 2 SPD 80kA", "each", "0.00", "0.50"),
    ("Surge Protection", "Type 2 SPD 140kA", "Generic", "Type 2 SPD 140kA", "each", "0.00", "0.60"),
    ("Surge Protection", "Generator Surge Protector", "Generic", "Generator SPD", "each", "0.00", "0.50"),
]


CATEGORY_RULES = [
    ("Panels", ["Panel", "Subpanel", "Meter", "Main Lug", "Load Center"]),
    ("Breakers", ["Breaker", "Interlock"]),
    ("Wire & Cable", ["Cable", "Wire", "THHN", "XHHW", "SER", "Conductor"]),
    ("Conduit", ["Conduit", "Raceway", "Service Mast"]),
    ("Fittings", ["Connector", "Coupling", "Adapter", "LB", "Bushing", "Locknut", "Strap", "Whip"]),
    ("Grounding & Bonding", ["Ground", "Bonding", "Bond"]),
    ("Boxes", ["Box", "Mud Ring", "Ceiling Box", "Fan Brace"]),
    ("Devices", ["Receptacle", "Switch", "Dimmer", "Timer", "Sensor", "Plate", "Cover"]),
    ("Lighting", ["Light", "Lighting", "Wafer", "Trim", "Chandelier", "Vanity", "Flood"]),
    ("Fans & Ventilation", ["Fan", "Exhaust"]),
    ("Low Voltage", ["Cat6", "Coax", "Doorbell", "Data", "Keystone", "Transformer"]),
    ("EV Charging", ["EV", "NEMA 14-50"]),
    ("Generator", ["Generator", "Transfer"]),
    ("Safety", ["Smoke", "CO Detector"]),
    ("Consumables", ["Tape", "Wire Nut", "Wago", "Staples", "Screws", "Anchors", "Caulk", "Duct Seal", "Anti-Ox", "Zip"]),
    ("Appliances", ["Dryer", "Range", "Dishwasher", "Disposal", "Water Heater", "Microwave"]),
]


class Command(BaseCommand):
    help = "Upgrade JCV material catalog to residential pricebook v2."

    def handle(self, *args, **kwargs):
        removed = 0
        created = 0
        updated = 0
        categorized = 0

        for name in MATERIALS_TO_REMOVE:
            deleted_count, _ = MaterialCatalog.objects.filter(name=name).delete()
            removed += deleted_count

        for category, name, manufacturer, part_number, unit, unit_cost, labor_hours in MATERIALS_TO_ADD:
            obj, was_created = MaterialCatalog.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "manufacturer": manufacturer,
                    "part_number": part_number,
                    "unit": unit,
                    "unit_cost": Decimal(unit_cost),
                    "labor_hours": Decimal(labor_hours),
                    "material_markup": Decimal("35.00"),
                    "supplier": "",
                    "active": True,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        for material in MaterialCatalog.objects.all():
            if material.category:
                continue

            matched_category = "Miscellaneous"

            for category, keywords in CATEGORY_RULES:
                if any(keyword.lower() in material.name.lower() for keyword in keywords):
                    matched_category = category
                    break

            material.category = matched_category
            material.save()
            categorized += 1

        self.stdout.write(self.style.SUCCESS("JCV material catalog v2 upgrade complete."))
        self.stdout.write(f"Removed allowance/template-only items: {removed}")
        self.stdout.write(f"Created new materials: {created}")
        self.stdout.write(f"Updated existing materials: {updated}")
        self.stdout.write(f"Categorized existing materials: {categorized}")