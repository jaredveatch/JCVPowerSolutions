import re


def qty_from_prompt(prompt, default=1):
    numbers = re.findall(r"\b\d+\b", prompt)
    return int(numbers[0]) if numbers else default


def material(name, qty=1, unit="each", reason="Needed for job."):
    return {
        "name": name,
        "qty": qty,
        "unit": unit,
        "reason": reason,
    }


def package(
    *,
    scenario,
    confidence="high",
    materials=None,
    steps=None,
    questions=None,
    labor_min=1,
    labor_max=3,
    customer_scope="",
    internal_notes="",
):
    return {
        "scenario": scenario,
        "confidence": confidence,
        "materials": materials or [],
        "steps": steps or [],
        "questions": questions or [],
        "labor_hours_min": labor_min,
        "labor_hours_max": labor_max,
        "customer_scope": customer_scope,
        "internal_notes": internal_notes,
    }


def lighting_steps():
    return [
        "Confirm fixture locations and customer expectations.",
        "Verify existing circuit and switch control.",
        "Turn off power and verify circuit is de-energized.",
        "Check for framing, ducts, plumbing, and obstructions.",
        "Install boxes/fixtures/wiring as required.",
        "Make safe electrical terminations.",
        "Restore power and test operation.",
        "Clean work area.",
    ]


def troubleshooting_steps():
    return [
        "Interview customer about when issue started.",
        "Identify all affected rooms, outlets, lights, or equipment.",
        "Check panel for tripped breakers or abnormal conditions.",
        "Check GFCI/AFCI devices if applicable.",
        "Test voltage and continuity where appropriate.",
        "Inspect devices for loose connections, burnt wiring, failed splices, or damage.",
        "Isolate load if breaker is tripping.",
        "Repair only after cause is confirmed and approved.",
        "Test circuit under normal load.",
        "Document findings.",
    ]


SCENARIOS = [
    {
        "name": "Soffit Lighting",
        "triggers": ["soffit", "soffit light", "soffit lights", "exterior recessed"],
        "builder": lambda p: package(
            scenario="Soffit Lighting",
            materials=[
                material("Exterior Rated LED Wafer Light", qty_from_prompt(p, 4)),
                material("14/2 NM-B Cable", max(75, qty_from_prompt(p, 4) * 20), "ft"),
                material("Weather Resistant Switch or Timer", 1),
                material("Exterior Rated Connectors / Consumables", 1, "allowance"),
            ],
            steps=lighting_steps(),
            questions=[
                "How many soffit lights?",
                "Existing switch or new switch?",
                "Attic access available?",
                "Customer wants timer, photocell, or smart switch?",
                "Are soffits open or finished?",
            ],
            labor_min=4,
            labor_max=8,
            customer_scope="Install exterior soffit lighting, route wiring, install controls, test operation, and clean work area.",
            internal_notes="Verify exterior rating, access, switch location, and drywall/soffit repair exclusions.",
        ),
    },
    {
        "name": "Recessed Lighting",
        "triggers": ["recessed", "can light", "wafer", "downlight", "led lights"],
        "builder": lambda p: package(
            scenario="Recessed Lighting",
            materials=[
                material("LED Wafer Recessed Light", qty_from_prompt(p, 4)),
                material("14/2 NM-B Cable", max(50, qty_from_prompt(p, 4) * 15), "ft"),
                material("LED Compatible Dimmer Switch", 1 if "dimmer" in p.lower() else 0),
                material("Wire Connectors", 1, "pack"),
                material("NM Staples / Consumables", 1, "allowance"),
            ],
            steps=lighting_steps(),
            questions=[
                "How many lights?",
                "Existing switch?",
                "Dimmer wanted?",
                "Attic access?",
                "Drywall repair included or excluded?",
            ],
            labor_min=max(2, qty_from_prompt(p, 4) // 2),
            labor_max=max(4, qty_from_prompt(p, 4) // 2 + 3),
            customer_scope="Install recessed LED lighting with wiring, controls, testing, and cleanup.",
            internal_notes="Confirm attic access and ceiling obstructions.",
        ),
    },
    {
        "name": "Vanity Light",
        "triggers": ["vanity", "bath light", "bathroom light"],
        "builder": lambda p: package(
            scenario="Vanity Light",
            materials=[
                material("Vanity Light Fixture", 1),
                material("Old Work Fixture Box", 1),
                material("Wire Connectors", 1, "pack"),
                material("Blank/Device Cover Plate", 1),
                material("Misc Consumables", 1, "allowance"),
            ],
            steps=lighting_steps(),
            questions=[
                "Customer supplied fixture?",
                "Existing box centered?",
                "Need box relocated?",
                "Wall repair included?",
            ],
            labor_min=1,
            labor_max=3,
            customer_scope="Replace or install bathroom vanity light fixture and test operation.",
            internal_notes="Many vanity jobs need box relocation due to mirror/cabinet alignment.",
        ),
    },
    {
        "name": "Chandelier",
        "triggers": ["chandelier", "hanging light", "foyer light"],
        "builder": lambda p: package(
            scenario="Chandelier",
            materials=[
                material("Fixture Rated Box / Support Hardware", 1),
                material("Wire Connectors", 1, "pack"),
                material("Misc Mounting Hardware", 1, "allowance"),
            ],
            steps=lighting_steps(),
            questions=[
                "Customer supplied chandelier?",
                "Ceiling height?",
                "Need ladder or scaffold?",
                "Existing box rated for weight?",
                "Assembly required?",
            ],
            labor_min=2,
            labor_max=5,
            customer_scope="Install chandelier or hanging fixture, verify support, connect wiring, test operation, and clean work area.",
            internal_notes="Confirm fixture weight and ceiling height before pricing.",
        ),
    },
    {
        "name": "Flood Light",
        "triggers": ["flood light", "floodlight", "security light", "motion light"],
        "builder": lambda p: package(
            scenario="Flood Light",
            materials=[
                material("Exterior Flood Light / Motion Light", 1),
                material("Weatherproof Box", 1),
                material("Weatherproof Cover / Gasket", 1),
                material("14/2 NM-B or UF Cable", 50, "ft"),
                material("Exterior Rated Connectors / Consumables", 1, "allowance"),
            ],
            steps=lighting_steps(),
            questions=[
                "Existing light location or new location?",
                "Motion sensor wanted?",
                "Switch controlled or constant power?",
                "Ladder height?",
            ],
            labor_min=2,
            labor_max=5,
            customer_scope="Install exterior flood/security light, route wiring as needed, test operation, and aim fixture.",
            internal_notes="Verify weatherproofing and access.",
        ),
    },
    {
        "name": "Ceiling Fan Replacement",
        "triggers": ["replace fan", "fan replacement", "replace ceiling fan"],
        "builder": lambda p: package(
            scenario="Ceiling Fan Replacement",
            materials=[
                material("Ceiling Fan Rated Box", 1),
                material("Wire Connectors", 1, "pack"),
                material("Misc Consumables", 1, "allowance"),
            ],
            steps=[
                "Confirm fan is customer supplied or contractor supplied.",
                "Turn off power and verify de-energized.",
                "Remove existing fan.",
                "Verify existing box is fan-rated.",
                "Replace support box if needed.",
                "Assemble and mount new fan.",
                "Make terminations.",
                "Test fan, light, and remote/control.",
                "Clean work area.",
            ],
            questions=[
                "Customer supplied fan?",
                "Existing box fan-rated?",
                "Remote control or wall control?",
                "Ceiling height?",
            ],
            labor_min=1,
            labor_max=3,
            customer_scope="Replace existing ceiling fan, verify safe support, connect wiring, test operation, and clean work area.",
            internal_notes="Do not reuse non-fan-rated boxes.",
        ),
    },
    {
        "name": "New Ceiling Fan Install",
        "triggers": ["new fan", "add fan", "install ceiling fan", "no fan"],
        "builder": lambda p: package(
            scenario="New Ceiling Fan Install",
            materials=[
                material("Ceiling Fan Rated Box / Brace Kit", 1),
                material("14/3 NM-B Cable", 75, "ft"),
                material("Single Gang Switch Box", 1),
                material("Fan/Light Switch", 1),
                material("Single Gang Cover Plate", 1),
                material("Wire Connectors / Consumables", 1, "allowance"),
            ],
            steps=[
                "Confirm fan location and switch location.",
                "Verify available circuit and attic/wall access.",
                "Turn off power and verify de-energized.",
                "Cut ceiling and switch openings as needed.",
                "Install fan-rated brace/box.",
                "Fish wiring from switch/circuit to fan location.",
                "Install switch/control.",
                "Mount fan and make terminations.",
                "Test fan/light operation.",
                "Clean work area.",
            ],
            questions=[
                "Attic access?",
                "Existing switch available?",
                "Separate fan/light control?",
                "Customer supplied fan?",
                "Drywall repair included?",
            ],
            labor_min=3,
            labor_max=6,
            customer_scope="Install new ceiling fan location with fan-rated support, wiring, switch/control, testing, and cleanup.",
            internal_notes="Drywall repair should be excluded unless included.",
        ),
    },
    {
        "name": "Dedicated Circuit",
        "triggers": ["dedicated circuit", "microwave circuit", "freezer circuit", "garage outlet", "20 amp circuit"],
        "builder": lambda p: package(
            scenario="Dedicated Circuit",
            confidence="medium",
            materials=[
                material("20A Single Pole Breaker", 1),
                material("12/2 NM-B Cable", 75, "ft"),
                material("20A Duplex Receptacle", 1),
                material("Electrical Box", 1),
                material("Cover Plate", 1),
                material("Wire Connectors / Staples / Consumables", 1, "allowance"),
            ],
            steps=[
                "Confirm equipment/load and location.",
                "Verify panel space and circuit capacity.",
                "Plan route from panel to new outlet.",
                "Install breaker, cable, box, and receptacle.",
                "Secure cable where accessible.",
                "Terminate conductors.",
                "Label panel.",
                "Test voltage and operation.",
            ],
            questions=[
                "What equipment is circuit for?",
                "How far from panel?",
                "Garage, kitchen, exterior, or other location?",
                "Panel full?",
                "Access through attic/crawl/garage?",
            ],
            labor_min=3,
            labor_max=6,
            customer_scope="Install new dedicated 120V circuit from panel to requested location, including breaker, wiring, receptacle, testing, and labeling.",
            internal_notes="Verify AFCI/GFCI requirements by location.",
        ),
    },
    {
        "name": "Mini Split Circuit",
        "triggers": ["mini split", "minisplit", "ac circuit", "hvac circuit"],
        "builder": lambda p: package(
            scenario="Mini Split Circuit",
            confidence="medium",
            materials=[
                material("2-Pole Breaker - Verify Amperage", 1),
                material("Cable Sized Per Equipment Nameplate", 75, "ft"),
                material("Non-Fused or Fused AC Disconnect", 1),
                material("Liquidtight Whip", 1),
                material("Exterior Rated Fasteners / Consumables", 1, "allowance"),
            ],
            steps=[
                "Confirm equipment nameplate voltage and MCA/MOCP.",
                "Verify panel capacity and breaker space.",
                "Plan route to outdoor condenser location.",
                "Install breaker, circuit wiring, disconnect, and whip.",
                "Terminate conductors.",
                "Label panel.",
                "Test voltage.",
            ],
            questions=[
                "What is the MCA/MOCP on the unit?",
                "Indoor or outdoor disconnect location?",
                "Distance from panel?",
                "Is unit already installed?",
            ],
            labor_min=4,
            labor_max=8,
            customer_scope="Install electrical circuit and disconnect for mini-split equipment based on manufacturer nameplate requirements.",
            internal_notes="Must verify nameplate before final wire/breaker sizing.",
        ),
    },
    {
        "name": "Dead Outlets",
        "triggers": ["dead outlet", "dead outlets", "outlets not working", "no power outlet"],
        "builder": lambda p: package(
            scenario="Dead Outlets Troubleshooting",
            confidence="medium",
            materials=[
                material("Standard Duplex Receptacle", 2),
                material("GFCI Receptacle", 1),
                material("Wire Connectors", 1, "pack"),
                material("Cover Plates", 2),
                material("Troubleshooting Consumables", 1, "allowance"),
            ],
            steps=troubleshooting_steps(),
            questions=[
                "One outlet or multiple outlets?",
                "Kitchen, bathroom, garage, exterior, or bedroom?",
                "Any GFCI tripped?",
                "Any recent work or storm?",
            ],
            labor_min=1,
            labor_max=3,
            customer_scope="Diagnose dead outlet issue, identify cause, and provide repair options.",
            internal_notes="Common causes: tripped GFCI, failed backstab, loose splice, bad device.",
        ),
    },
    {
        "name": "Tripping Breaker",
        "triggers": ["tripping breaker", "breaker trips", "keeps tripping", "trip breaker"],
        "builder": lambda p: package(
            scenario="Tripping Breaker Troubleshooting",
            confidence="medium",
            materials=[
                material("Matching Breaker - Verify Panel Type", 1),
                material("Standard Duplex Receptacle", 2),
                material("Wire Connectors", 1, "pack"),
                material("Troubleshooting Consumables", 1, "allowance"),
            ],
            steps=troubleshooting_steps(),
            questions=[
                "Trips instantly or after load is used?",
                "What appliance/device is being used?",
                "AFCI/GFCI breaker?",
                "Any burning smell or buzzing?",
            ],
            labor_min=1,
            labor_max=4,
            customer_scope="Diagnose breaker tripping issue, isolate fault/load, and provide repair options.",
            internal_notes="Do not replace breaker until load/fault is diagnosed.",
        ),
    },
    {
        "name": "Flickering Lights",
        "triggers": ["flickering", "lights flicker", "flicker"],
        "builder": lambda p: package(
            scenario="Flickering Lights Troubleshooting",
            confidence="medium",
            materials=[
                material("Switch", 1),
                material("Wire Connectors", 1, "pack"),
                material("Compatible Dimmer - If Needed", 1),
                material("Troubleshooting Consumables", 1, "allowance"),
            ],
            steps=troubleshooting_steps(),
            questions=[
                "One light or whole house?",
                "Only when appliance starts?",
                "LED bulbs on dimmer?",
                "Any panel buzzing or burning smell?",
            ],
            labor_min=1,
            labor_max=4,
            customer_scope="Diagnose flickering light issue and provide repair options.",
            internal_notes="Whole-house flicker may require utility/service investigation.",
        ),
    },
    {
        "name": "Partial Power Loss",
        "triggers": ["partial power", "half power", "half the house", "lost power"],
        "builder": lambda p: package(
            scenario="Partial Power Loss",
            confidence="medium",
            materials=[
                material("Troubleshooting Consumables", 1, "allowance"),
                material("Wire Connectors", 1, "pack"),
            ],
            steps=troubleshooting_steps(),
            questions=[
                "Is it half the house or one room?",
                "Any 240V appliances not working?",
                "Any recent storms?",
                "Any breakers loose or hot?",
            ],
            labor_min=1,
            labor_max=4,
            customer_scope="Diagnose partial power loss and identify whether issue is branch circuit, panel, service, or utility related.",
            internal_notes="Possible lost leg/service issue. Treat seriously.",
        ),
    },
    {
        "name": "Kitchen Remodel",
        "triggers": ["kitchen remodel", "kitchen renovation", "remodel kitchen"],
        "builder": lambda p: package(
            scenario="Kitchen Remodel Electrical",
            materials=[
                material("20A GFCI/AFCI Kitchen Circuit Materials", 2, "allowance"),
                material("12/2 NM-B Cable", 200, "ft"),
                material("GFCI Receptacles", 2),
                material("Tamper Resistant Receptacles", 8),
                material("Device Boxes", 10),
                material("Switches / Plates / Consumables", 1, "allowance"),
            ],
            steps=[
                "Review kitchen layout and appliance locations.",
                "Identify required small appliance circuits.",
                "Plan lighting, switching, disposal, dishwasher, microwave, range/hood circuits.",
                "Rough-in boxes and wiring.",
                "Coordinate inspection if required.",
                "Trim devices and fixtures after finishes.",
                "Test and label circuits.",
            ],
            questions=[
                "New layout available?",
                "Appliance list?",
                "Island or peninsula?",
                "Under-cabinet lighting?",
                "Permit/inspection required?",
            ],
            labor_min=12,
            labor_max=30,
            customer_scope="Provide electrical rough-in and trim-out for kitchen remodel based on final layout and appliance requirements.",
            internal_notes="Needs layout. Price rough-in and trim-out separately if possible.",
        ),
    },
    {
        "name": "Bathroom Remodel",
        "triggers": ["bathroom remodel", "bath remodel", "bathroom renovation"],
        "builder": lambda p: package(
            scenario="Bathroom Remodel Electrical",
            materials=[
                material("20A Bathroom GFCI Circuit Materials", 1, "allowance"),
                material("12/2 NM-B Cable", 75, "ft"),
                material("GFCI Receptacle", 1),
                material("Vanity Light Box", 1),
                material("Exhaust Fan / Fan-Light Materials", 1, "allowance"),
                material("Switches / Plates / Consumables", 1, "allowance"),
            ],
            steps=[
                "Review bathroom layout.",
                "Confirm vanity, fan, lighting, and receptacle locations.",
                "Rough-in wiring and boxes.",
                "Coordinate inspection if required.",
                "Install devices, lights, and fan after finishes.",
                "Test GFCI and operation.",
            ],
            questions=[
                "Moving vanity?",
                "New exhaust fan?",
                "Shower light?",
                "Dedicated 20A bathroom circuit needed?",
                "Permit required?",
            ],
            labor_min=6,
            labor_max=16,
            customer_scope="Provide electrical rough-in and trim-out for bathroom remodel.",
            internal_notes="Confirm fan ducting responsibility and drywall exclusions.",
        ),
    },
    {
        "name": "Addition / Garage Conversion",
        "triggers": ["addition", "garage conversion", "convert garage", "room addition"],
        "builder": lambda p: package(
            scenario="Addition / Garage Conversion Electrical",
            confidence="medium",
            materials=[
                material("Branch Circuit Wiring Allowance", 1, "allowance"),
                material("Receptacles / Switches / Boxes", 1, "allowance"),
                material("Lighting Materials", 1, "allowance"),
                material("Smoke/CO Detector Materials", 1, "allowance"),
                material("Panel Breakers - Verify Type", 1, "allowance"),
            ],
            steps=[
                "Review plans/layout.",
                "Determine required circuits, outlets, lighting, smoke/CO, HVAC loads.",
                "Verify panel capacity and available breaker space.",
                "Rough-in wiring and boxes.",
                "Coordinate inspection if required.",
                "Trim devices and fixtures.",
                "Test and label circuits.",
            ],
            questions=[
                "Do you have plans?",
                "Bedroom, office, living space, or garage?",
                "HVAC/mini-split included?",
                "Panel capacity available?",
                "Permit required?",
            ],
            labor_min=12,
            labor_max=40,
            customer_scope="Provide electrical rough-in and trim-out for addition or garage conversion based on approved layout.",
            internal_notes="Needs site visit/plans before fixed price.",
        ),
    },
]


def find_best_scenario(prompt):
    prompt_lower = prompt.lower().strip()

    for scenario in SCENARIOS:
        for trigger in scenario["triggers"]:
            if trigger in prompt_lower:
                return scenario["builder"](prompt)

    return package(
        scenario="Custom Electrical Job",
        confidence="low",
        materials=[
            material("Misc Electrical Materials", 1, "allowance"),
            material("Wire Connectors / Consumables", 1, "allowance"),
        ],
        steps=[
            "Review customer request.",
            "Identify whether this is install, replacement, troubleshooting, or remodel work.",
            "Verify existing electrical conditions.",
            "Confirm circuit requirements and access.",
            "Build final material list after site verification.",
            "Complete work after customer approval.",
            "Test operation and document findings.",
        ],
        questions=[
            "What exactly needs to be installed, replaced, or diagnosed?",
            "Is there existing power at the location?",
            "What room/location is this in?",
            "Is attic, crawlspace, garage, or wall access available?",
            "Is the customer supplying any materials?",
        ],
        labor_min=1,
        labor_max=4,
        customer_scope=prompt,
        internal_notes="No exact scenario matched. JARVIS created a general electrical job checklist.",
    )