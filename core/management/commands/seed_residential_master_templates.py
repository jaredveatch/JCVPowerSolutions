from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import ServiceTemplate


MASTER_TEMPLATES = [
    (
        "Diagnostic & Troubleshooting",
        "Diagnostic & Troubleshooting",
        "Electrical diagnostic service for power loss, tripping breakers, flickering lights, dead outlets, burning smell concerns, and unknown electrical issues.",
        "Verify symptoms, inspect affected devices/circuits, test voltage, inspect panel/breakers, identify likely cause, explain repair options, and document findings.",
        "1.50",
        "🔎",
    ),
    (
        "Panel & Service Work",
        "Panel & Service Upgrades",
        "Panel replacement, 100A/150A/200A upgrades, indoor/outdoor panels, meter equipment, service entrance repairs, and utility coordination.",
        "Verify service size, load requirements, panel location, working clearance, grounding/bonding, utility requirements, permits, breaker compatibility, labeling, torque specs, and inspection requirements.",
        "8.00",
        "⚡",
    ),
    (
        "Grounding & Bonding",
        "Grounding & Bonding",
        "Ground rod installation, water bonding, intersystem bonding, grounding electrode upgrades, and service bonding corrections.",
        "Verify existing grounding electrode system, water bond, intersystem bond, conductor sizing, clamps, accessibility, corrosion, and code/inspection requirements.",
        "2.00",
        "⛓️",
    ),
    (
        "Dedicated Circuits",
        "Dedicated Circuits",
        "Dedicated 120V or 240V circuits for appliances, equipment, garages, workshops, HVAC, refrigerators, microwaves, dryers, ranges, and specialty loads.",
        "Verify load, amperage, voltage, breaker size, conductor size, routing, panel capacity, AFCI/GFCI requirements, receptacle/disconnect type, labeling, and customer-approved location.",
        "3.00",
        "🔌",
    ),
    (
        "EV Charging",
        "EV Charger Installation",
        "Level 2 EV charger installation, Tesla Wall Connector, customer-supplied chargers, hardwired chargers, NEMA receptacles, and EV load calculations.",
        "Verify charger specs, load calculation, panel capacity, breaker size, conductor size, routing, GFCI requirements, mounting location, commissioning, labeling, and permit requirements.",
        "4.00",
        "🚗",
    ),
    (
        "Generator & Backup Power",
        "Generator & Backup Power",
        "Portable generator inlets, interlock kits, transfer switches, standby generator preparation, and backup power troubleshooting.",
        "Verify generator size, panel compatibility, interlock/transfer method, inlet location, conductor sizing, grounding/bonding, labeling, load planning, and inspection requirements.",
        "5.00",
        "🔋",
    ),
    (
        "Receptacles & Power Devices",
        "Receptacles & Power Devices",
        "Outlet replacement, new outlets, GFCI/AFCI devices, USB outlets, weather-resistant outlets, floor outlets, and 240V receptacles.",
        "Verify device type, box condition, grounding, polarity, GFCI/AFCI requirements, box fill, secure mounting, cover plate, and proper operation.",
        "1.00",
        "🔘",
    ),
    (
        "Switches & Controls",
        "Switches & Controls",
        "Switch replacements, new switches, three-way/four-way switches, dimmers, timers, motion sensors, smart switches, and fan controls.",
        "Verify wiring configuration, switch leg, neutral availability, device compatibility, box fill, grounding, labeling, and proper operation.",
        "1.00",
        "🎚️",
    ),
    (
        "Lighting",
        "Lighting Installation & Repair",
        "Fixture replacement, new lighting, chandeliers, pendants, vanity lights, exterior fixtures, security lights, flood lights, and LED upgrades.",
        "Verify fixture location, box support, ladder/access needs, switch control, dimmer compatibility, customer-supplied parts, mounting, and proper operation.",
        "2.00",
        "💡",
    ),
    (
        "Recessed Lighting",
        "Recessed Lighting",
        "Wafer lights, remodel cans, recessed lighting layouts, LED conversions, and room lighting upgrades.",
        "Verify layout, ceiling access, insulation rating, switch/dimmer controls, spacing, wiring route, customer-approved locations, and patching exclusions.",
        "4.00",
        "🔦",
    ),
    (
        "Ceiling Fans & Ventilation",
        "Ceiling Fans & Ventilation",
        "Ceiling fan installation, fan replacement, fan-rated boxes, fan controls, bathroom exhaust fans, and ventilation electrical connections.",
        "Verify fan-rated support, ceiling height, switch control, remote receiver, customer-supplied parts, venting requirements for bath fans, and proper operation.",
        "2.00",
        "🌀",
    ),
    (
        "Smoke & Life Safety",
        "Smoke & Life Safety",
        "Smoke detectors, smoke/CO detectors, interconnected systems, detector replacement, and safety upgrades.",
        "Verify detector type, power source, interconnection, placement, age of existing devices, code requirements, and testing.",
        "2.00",
        "🚨",
    ),
    (
        "Smart Home",
        "Smart Home Electrical",
        "Smart thermostats, smart doorbells, smart lighting controls, smart switches, home automation devices, and device power support.",
        "Verify device compatibility, power requirements, neutral availability, transformer needs, Wi-Fi/customer setup expectations, and proper operation.",
        "1.50",
        "🏠",
    ),
    (
        "Low Voltage & Communications",
        "Low Voltage & Communications",
        "CAT6/data drops, TV outlets, camera wiring, network wiring, doorbell wiring, and low-voltage device support.",
        "Verify cable route, device location, separation from line voltage, wall access, termination type, testing, and customer equipment requirements.",
        "2.00",
        "📡",
    ),
    (
        "Exterior Electrical",
        "Exterior Electrical",
        "Exterior outlets, patio power, exterior lighting, shed power, detached garage feeders, security lighting, and holiday lighting receptacles.",
        "Verify weatherproof equipment, GFCI protection, burial/routing requirements, conduit type, mounting, location, and weather-resistant covers.",
        "3.00",
        "🌳",
    ),
    (
        "Landscape Lighting",
        "Landscape & Specialty Lighting",
        "Landscape lighting, path lights, accent lights, transformers, low-voltage lighting controls, and outdoor lighting upgrades.",
        "Verify transformer location, load, low-voltage cable route, fixture layout, controls/timer, GFCI protection, and customer-approved placement.",
        "3.00",
        "🌙",
    ),
    (
        "Appliance Connections",
        "Appliance Connections",
        "Dishwasher, disposal, microwave, oven, dryer, range, refrigerator, hood vent, and appliance electrical connections or circuits.",
        "Verify appliance specs, voltage, amperage, breaker size, conductor size, receptacle/disconnect type, location, and manufacturer requirements.",
        "2.50",
        "🍳",
    ),
    (
        "Pools, Spas & Outdoor Equipment",
        "Pools, Spas & Outdoor Equipment",
        "Hot tubs, pool equipment, pool lights, disconnects, bonding, pumps, and outdoor equipment electrical work.",
        "Verify equipment specs, disconnect location, GFCI protection, bonding requirements, conductor sizing, trenching/routing, and inspection requirements.",
        "5.00",
        "🏊",
    ),
    (
        "Remodels & Additions",
        "Remodels & Additions",
        "Kitchen remodels, bathroom remodels, room additions, garage conversions, basement finishes, and whole-room wiring updates.",
        "Review plans, device layout, lighting layout, circuit requirements, AFCI/GFCI needs, permits, rough-in, trim-out, inspections, and customer selections.",
        "8.00",
        "🧱",
    ),
    (
        "Wiring Repairs & Rewiring",
        "Wiring Repairs & Rewiring",
        "Damaged wiring repairs, aluminum wiring corrections, partial rewires, whole-home rewires, and unsafe wiring replacement.",
        "Identify wiring type, damage, access, circuit impact, code requirements, repair method, junction box needs, labeling, and testing.",
        "4.00",
        "🧰",
    ),
    (
        "Code Corrections",
        "Code Corrections",
        "Home inspection repairs, insurance corrections, NEC deficiencies, safety corrections, and real estate electrical repairs.",
        "Review inspection report, verify issue on site, determine correction method, document completed repairs, and note permit/inspection requirements when applicable.",
        "3.00",
        "📋",
    ),
    (
        "Home Electrical Inspections",
        "Home Electrical Inspections",
        "Buyer inspections, seller inspections, annual safety inspections, insurance inspections, and general electrical condition reports.",
        "Inspect panel, grounding, bonding, visible wiring, devices, GFCI/AFCI protection, smoke detectors, exterior electrical, and provide findings.",
        "2.50",
        "🏡",
    ),
    (
        "Surge Protection",
        "Surge Protection",
        "Whole-home surge protection, surge protector replacement, point-of-use protection recommendations, and surge troubleshooting.",
        "Verify panel compatibility, breaker space, device rating, grounding/bonding, installation location, labeling, and customer education.",
        "1.50",
        "🛡️",
    ),
    (
        "Permit & Utility Coordination",
        "Permit & Utility Coordination",
        "Permit pulling, utility disconnect/reconnect, inspection coordination, service release, and administrative coordination for electrical work.",
        "Confirm jurisdiction, permit scope, utility requirements, inspection requirements, scheduling, documentation, and closeout needs.",
        "1.00",
        "🏛️",
    ),
    (
        "Custom Electrical Work",
        "Custom Electrical Work",
        "Custom homeowner electrical requests, specialty projects, unusual installations, and work that does not fit a standard template.",
        "Document customer request, inspect conditions, define scope, identify materials, confirm exclusions, price labor/materials, and verify code/permit requirements.",
        "2.00",
        "✨",
    ),
]


class Command(BaseCommand):
    help = "Seed clean generalized residential master service templates."

    def handle(self, *args, **kwargs):
        created = 0
        updated = 0

        for category, name, description, checklist, labor_hours, icon in MASTER_TEMPLATES:
            template, was_created = ServiceTemplate.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "customer_description": description,
                    "internal_checklist": checklist,
                    "default_labor_hours": Decimal(labor_hours),
                    "labor_rate": Decimal("125.00"),
                    "estimated_material_cost": Decimal("0.00"),
                    "material_markup": Decimal("35.00"),
                    "default_price": Decimal("0.00"),
                    "permit_required": False,
                    "active": True,
                    "icon": icon,
                    "notes": "Master residential service template. Use options/material packages for specific job variations.",
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Residential master templates seeded. Created {created}. Updated {updated}."
            )
        )