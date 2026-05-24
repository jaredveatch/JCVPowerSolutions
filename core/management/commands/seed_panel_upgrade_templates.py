from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import (
    MaterialCatalog,
    ServiceTemplate,
    ServiceTemplateMaterial,
)


class Command(BaseCommand):
    help = "Seed clean organized residential electrical service templates."

    def get_material(self, name):
        material, created = MaterialCatalog.objects.get_or_create(
            name=name,
            defaults={
                "manufacturer": "Generic",
                "part_number": "",
                "unit": "each",
                "unit_cost": Decimal("0.00"),
                "labor_hours": Decimal("0.00"),
                "active": True,
            },
        )

        material.active = True
        material.save()

        return material

    def add_materials(self, template, material_names):
        for material_name in material_names:
            material = self.get_material(material_name)

            ServiceTemplateMaterial.objects.update_or_create(
                service_template=template,
                material=material,
                defaults={
                    "quantity": Decimal("1"),
                },
            )

    def create_template(
        self,
        category,
        name,
        description,
        checklist,
        materials=None,
        labor_hours="0.00",
        icon="⚡",
    ):
        template, created = ServiceTemplate.objects.update_or_create(
            name=name,
            defaults={
                "category": category,
                "customer_description": description,
                "internal_checklist": checklist,
                "default_labor_hours": Decimal(labor_hours),
                "default_price": Decimal("0.00"),
                "active": True,
                "icon": icon,
            },
        )

        if materials:
            self.add_materials(template, materials)

        return template

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding clean residential templates...")

        # =====================================================
        # PANEL / SERVICE WORK
        # =====================================================

        panel_checklist = (
            "Verify existing service size, utility requirements, meter/main setup, "
            "panel location, working clearance, grounding electrode system, bonding, "
            "permit requirements, load calculation, breaker compatibility, labeling, "
            "torque specs, and inspection requirements."
        )

        panel_materials = [
            "Square D Homeline Main Breaker Panel",
            "Square D Homeline 15A Single Pole Breaker",
            "Square D Homeline 20A Single Pole Breaker",
            "Square D Homeline 30A Two Pole Breaker",
            "Square D Homeline 40A Two Pole Breaker",
            "Square D Homeline 50A Two Pole Breaker",
            "Square D Homeline Ground Bar Kit",
            "Square D Homeline Filler Plates",
            "Square D Homeline Whole Home Surge Protector",
            "Service Entrance Conductors",
            "#6 Bare Copper Ground Wire",
            "8 ft Ground Rod",
            "Ground Rod Clamp",
            "Intersystem Bonding Bridge",
            "Water Pipe Ground Clamp",
            "PVC Conduit",
            "PVC Male Adapter",
            "PVC Coupling",
            "PVC Strap",
            "Bonding Bushing",
            "Anti-Ox Compound",
            "Duct Seal",
            "Electrical Tape",
            "Panel Directory Labels",
        ]

        panel_templates = [
            "100A Panel Install - Indoor",
            "100A Panel Install - Outdoor",
            "150A Panel Install - Indoor",
            "150A Panel Install - Outdoor",
            "200A Panel Install - Indoor",
            "200A Panel Install - Outdoor",
            "Meter/Main Combo Replacement",
            "Overhead Service Upgrade",
            "Underground Service Upgrade",
            "Whole Home Surge Protector Install",
            "Panel Tune-Up / Breaker Cleanup",
            "Breaker Replacement",
            "Grounding Electrode System Upgrade",
        ]

        for name in panel_templates:
            self.create_template(
                category="Panel / Service Work",
                name=name,
                description="Residential panel, service, breaker, grounding, or surge protection work.",
                checklist=panel_checklist,
                materials=panel_materials,
                labor_hours="8.00",
                icon="⚡",
            )

        # =====================================================
        # SUBPANELS
        # =====================================================

        subpanel_checklist = (
            "Verify feeder size, breaker size, panel rating, neutral isolation, "
            "ground bar installation, grounding path, working clearance, panel location, "
            "load requirements, labeling, and inspection requirements."
        )

        subpanel_materials = [
            "Main Lug Subpanel",
            "Two Pole Feeder Breaker",
            "Feeder Conductors",
            "Equipment Grounding Conductor",
            "Ground Bar Kit",
            "PVC Conduit",
            "PVC Male Adapter",
            "PVC Coupling",
            "PVC Strap",
            "Panel Directory Labels",
            "Electrical Tape",
        ]

        subpanel_templates = [
            "60A Subpanel Install - Indoor",
            "60A Subpanel Install - Outdoor",
            "100A Subpanel Install - Indoor",
            "100A Subpanel Install - Outdoor",
            "125A Subpanel Install - Indoor",
            "125A Subpanel Install - Outdoor",
        ]

        for name in subpanel_templates:
            self.create_template(
                category="Subpanels",
                name=name,
                description="Install residential subpanel with feeder, breaker, grounding, neutral isolation, and labeling.",
                checklist=subpanel_checklist,
                materials=subpanel_materials,
                labor_hours="6.00",
                icon="🧰",
            )

        # =====================================================
        # DEDICATED CIRCUITS
        # =====================================================

        circuit_checklist = (
            "Verify load, breaker size, conductor size, routing, panel capacity, "
            "AFCI/GFCI requirements, receptacle type, box fill, labeling, and "
            "customer-approved location."
        )

        dedicated_circuit_templates = [
            "15A Dedicated Circuit",
            "20A Dedicated Circuit",
            "30A Dedicated Circuit",
            "40A Dedicated Circuit",
            "50A Dedicated Circuit",
            "EV Charger Circuit",
            "RV Outlet Install",
            "Portable Generator Inlet Install",
            "Interlock Kit Install",
            "Manual Transfer Switch Install",
            "Standby Generator Electrical Hookup",
        ]

        dedicated_circuit_materials = [
            "Single Pole Breaker",
            "Two Pole Breaker",
            "GFCI Breaker",
            "NM-B Cable",
            "THHN Conductors",
            "PVC Conduit",
            "Electrical Box",
            "Receptacle",
            "Device Cover Plate",
            "Wire Staples",
            "Wire Connectors",
            "Electrical Tape",
            "Circuit Label",
        ]

        for name in dedicated_circuit_templates:
            self.create_template(
                category="Dedicated Circuits",
                name=name,
                description="Install dedicated residential branch circuit or equipment circuit.",
                checklist=circuit_checklist,
                materials=dedicated_circuit_materials,
                labor_hours="3.00",
                icon="🔌",
            )

        # =====================================================
        # OUTLETS / SWITCHES
        # =====================================================

        device_checklist = (
            "Verify existing wiring condition, box fill, grounding, device rating, "
            "GFCI/AFCI requirements, correct polarity, secure mounting, cover plate, "
            "and proper operation."
        )

        outlet_switch_templates = [
            "Standard Outlet Replacement",
            "Tamper Resistant Outlet Replacement",
            "GFCI Outlet Replacement",
            "USB Outlet Install",
            "Smart Outlet Install",
            "Outdoor GFCI Outlet Install",
            "Garage GFCI Outlet Install",
            "Weatherproof Outlet Install",
            "Add New Outlet - Existing Circuit",
            "Quad Outlet Install",
            "Light Switch Replacement",
            "Dimmer Switch Install",
            "Smart Switch Install",
            "Three Way Switch Replacement",
            "Four Way Switch Replacement",
            "Timer Switch Install",
            "Motion Sensor Switch Install",
        ]

        outlet_switch_materials = [
            "Duplex Receptacle",
            "Tamper Resistant Receptacle",
            "GFCI Receptacle",
            "WR GFCI Receptacle",
            "USB Receptacle",
            "Smart Receptacle",
            "Single Pole Light Switch",
            "Three Way Light Switch",
            "Four Way Light Switch",
            "Dimmer Switch",
            "Smart Switch",
            "Timer Switch",
            "Motion Sensor Switch",
            "Single Gang Old Work Box",
            "Two Gang Old Work Box",
            "Weatherproof Box",
            "In-Use Weatherproof Cover",
            "Device Cover Plate",
            "Wire Connectors",
            "Electrical Tape",
        ]

        for name in outlet_switch_templates:
            self.create_template(
                category="Outlets / Switches",
                name=name,
                description="Install, replace, or repair residential outlet, switch, dimmer, smart device, or weatherproof device.",
                checklist=device_checklist,
                materials=outlet_switch_materials,
                labor_hours="1.00",
                icon="🔘",
            )

        # =====================================================
        # LIGHTING
        # =====================================================

        lighting_checklist = (
            "Verify fixture location, box support, ceiling/wall access, switch control, "
            "dimmer compatibility, insulation rating, customer-approved layout, ladder access, "
            "and proper operation."
        )

        lighting_templates = [
            "Light Fixture Replacement",
            "Vanity Light Install",
            "Pendant Light Install",
            "Chandelier Install",
            "Recessed Lighting Install",
            "Under Cabinet Lighting Install",
            "LED Strip Lighting Install",
            "Exterior Flood Light Install",
            "Security Light Install",
            "Motion Light Install",
            "Garage Lighting Install",
            "Shop Lighting Install",
            "Attic Light Install",
            "Landscape Lighting Transformer Install",
        ]

        lighting_materials = [
            "Customer Supplied Light Fixture",
            "LED Wafer Recessed Light",
            "Exterior LED Flood Light",
            "Security Light",
            "Motion Sensor Light",
            "Under Cabinet LED Light",
            "LED Strip Light",
            "Landscape Lighting Transformer",
            "Fixture Mounting Bracket",
            "Light Switch",
            "Dimmer Switch",
            "Single Gang Old Work Box",
            "Switch Cover Plate",
            "14/2 NM-B Cable",
            "14/3 NM-B Cable",
            "Wire Staples",
            "Wire Connectors",
            "Electrical Tape",
        ]

        for name in lighting_templates:
            self.create_template(
                category="Lighting",
                name=name,
                description="Install, replace, or modify residential lighting.",
                checklist=lighting_checklist,
                materials=lighting_materials,
                labor_hours="2.00",
                icon="💡",
            )

        # =====================================================
        # FANS
        # =====================================================

        fan_checklist = (
            "Verify fan-rated box, support, ceiling height, switch control, remote receiver, "
            "blade clearance, customer-supplied parts, ducting if applicable, and proper operation."
        )

        fan_templates = [
            "Ceiling Fan Install - Existing Fan Box",
            "Ceiling Fan Install - New Fan Box",
            "Ceiling Fan Replacement",
            "Bathroom Exhaust Fan Replacement",
            "Bathroom Exhaust Fan New Install",
            "Attic Fan Install",
        ]

        fan_materials = [
            "Customer Supplied Ceiling Fan",
            "Fan Rated Ceiling Box",
            "Fan Control Switch",
            "Bathroom Exhaust Fan",
            "Attic Fan",
            "14/2 NM-B Cable",
            "14/3 NM-B Cable",
            "Single Gang Old Work Box",
            "Switch Cover Plate",
            "Foil HVAC Tape",
            "Wire Staples",
            "Wire Connectors",
            "Electrical Tape",
        ]

        for name in fan_templates:
            self.create_template(
                category="Fans",
                name=name,
                description="Install or replace ceiling fan, bathroom exhaust fan, or attic fan.",
                checklist=fan_checklist,
                materials=fan_materials,
                labor_hours="2.00",
                icon="🌀",
            )

        # =====================================================
        # TROUBLESHOOTING
        # =====================================================

        self.create_template(
            category="Troubleshooting",
            name="Troubleshooting Level 1 - Basic Diagnostic",
            description=(
                "Basic diagnostic for a simple issue usually isolated to one device, "
                "one room, or one obvious problem area."
            ),
            checklist=(
                "Use for single outlet not working, single switch issue, one light fixture out, "
                "simple GFCI reset, minor loose connection, basic voltage testing, or simple device replacement."
            ),
            materials=[
                "Troubleshooting Labor",
                "Duplex Receptacle",
                "GFCI Receptacle",
                "Light Switch",
                "Wire Connectors",
                "Electrical Tape",
            ],
            labor_hours="1.00",
            icon="🔎",
        )

        self.create_template(
            category="Troubleshooting",
            name="Troubleshooting Level 2 - Intermediate Diagnostic",
            description=(
                "Intermediate diagnostic requiring extended testing, multiple device inspections, "
                "circuit tracing, or partial system evaluation."
            ),
            checklist=(
                "Use for multiple outlets or lights affected, breaker repeatedly tripping, flickering lights, "
                "partial power loss, hidden loose neutral investigation, circuit overload investigation, "
                "intermittent problems, outdoor/garage faults, multi-location switching issues, or dedicated circuit diagnostics."
            ),
            materials=[
                "Troubleshooting Labor",
                "Replacement Breaker",
                "Duplex Receptacle",
                "GFCI Receptacle",
                "Light Switch",
                "Wire Connectors",
                "Electrical Tape",
                "Circuit Label",
            ],
            labor_hours="2.50",
            icon="🔎",
        )

        self.create_template(
            category="Troubleshooting",
            name="Troubleshooting Level 3 - Advanced Diagnostic",
            description=(
                "Advanced diagnostic for complex system issues, concealed wiring problems, "
                "service/panel investigation, or extensive fault tracing."
            ),
            checklist=(
                "Use for underground fault investigation, panel/service failure diagnostics, burnt wiring, "
                "aluminum wiring issues, major intermittent faults, whole-home power issues, utility coordination, "
                "large-scale circuit tracing, heat damage, water/fire damaged electrical systems, or unknown remodel wiring."
            ),
            materials=[
                "Troubleshooting Labor",
                "Replacement Breaker",
                "Wire Connectors",
                "Electrical Tape",
                "Circuit Label",
                "Panel Directory Labels",
            ],
            labor_hours="4.00",
            icon="🔎",
        )

        # =====================================================
        # LOW VOLTAGE
        # =====================================================

        low_voltage_checklist = (
            "Verify device requirements, power source, low-voltage path, separation from line voltage, "
            "customer-approved location, compatibility, mounting, and testing."
        )

        low_voltage_templates = [
            "Doorbell Transformer Replacement",
            "Smart Doorbell Install",
            "TV Outlet / Low Voltage Brush Plate",
            "Ethernet Drop Install",
            "Camera Power Install",
            "Wi-Fi Access Point Outlet Install",
            "Low Voltage Wire Repair",
        ]

        low_voltage_materials = [
            "Doorbell Transformer",
            "Smart Doorbell",
            "Recessed TV Outlet Kit",
            "Low Voltage Brush Plate",
            "Cat6 Cable",
            "Ethernet Jack",
            "Low Voltage Mounting Bracket",
            "Camera Power Supply",
            "Single Gang Old Work Box",
            "Wire Connectors",
            "Electrical Tape",
        ]

        for name in low_voltage_templates:
            self.create_template(
                category="Low Voltage",
                name=name,
                description="Install or repair residential low-voltage wiring or device support.",
                checklist=low_voltage_checklist,
                materials=low_voltage_materials,
                labor_hours="1.50",
                icon="📡",
            )

        self.stdout.write(
            self.style.SUCCESS("Clean organized residential templates seeded successfully.")
        )