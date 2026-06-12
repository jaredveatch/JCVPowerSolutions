from decimal import Decimal, ROUND_HALF_UP


D = Decimal


def money(value):
    return D(str(value or 0)).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def watts_to_amps(watts, voltage=240):
    watts = D(str(watts or 0))
    voltage = D(str(voltage or 240))

    if voltage <= 0:
        return D("0.00")

    return (watts / voltage).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def amps_to_watts(amps, voltage=240):
    return D(str(amps or 0)) * D(str(voltage or 240))


def residential_general_lighting_load(square_feet):
    return D(str(square_feet or 0)) * D("3")


def apply_standard_dwelling_demand(general_load_watts):
    """
    Simplified residential demand logic:
    - First 10,000W at 100%
    - Remainder at 40%

    This is an estimating helper, not a stamped calculation.
    """
    general_load_watts = D(str(general_load_watts or 0))

    if general_load_watts <= D("10000"):
        return general_load_watts

    return D("10000") + ((general_load_watts - D("10000")) * D("0.40"))


def appliance_demand(appliance_watts):
    """
    Simplified fixed appliance demand:
    - 1 to 3 appliances: 100%
    - 4 or more appliances: 75%

    This is a practical estimating approximation.
    """
    appliance_watts = [D(str(w or 0)) for w in appliance_watts if D(str(w or 0)) > 0]

    if not appliance_watts:
        return D("0.00")

    total = sum(appliance_watts, D("0.00"))

    if len(appliance_watts) >= 4:
        return total * D("0.75")

    return total


def range_demand(range_watts):
    """
    Simplified range allowance.
    Many residential ranges are commonly estimated around 8kW demand
    for pre-check purposes unless exact nameplate/design method is used.
    """
    range_watts = D(str(range_watts or 0))

    if range_watts <= 0:
        return D("0.00")

    if range_watts <= D("12000"):
        return D("8000")

    return D("8000") + ((range_watts - D("12000")) * D("0.40"))


def dryer_demand(dryer_watts):
    dryer_watts = D(str(dryer_watts or 0))

    if dryer_watts <= 0:
        return D("0.00")

    return max(dryer_watts, D("5000"))


def largest_hvac_load(cooling_watts=0, heating_watts=0, heat_pump_watts=0):
    loads = [
        D(str(cooling_watts or 0)),
        D(str(heating_watts or 0)),
        D(str(heat_pump_watts or 0)),
    ]
    return max(loads)


def service_recommendation(calculated_amps):
    amps = D(str(calculated_amps or 0))

    if amps <= D("80"):
        return {
            "recommended_service_amps": 100,
            "recommendation": "100A service may be sufficient, but verify future loads.",
        }

    if amps <= D("160"):
        return {
            "recommended_service_amps": 200,
            "recommendation": "200A service recommended.",
        }

    if amps <= D("200"):
        return {
            "recommended_service_amps": 225,
            "recommendation": "225A service or carefully reviewed 200A service may be needed.",
        }

    if amps <= D("320"):
        return {
            "recommended_service_amps": 320,
            "recommendation": "320A/400A class service should be reviewed.",
        }

    return {
        "recommended_service_amps": 400,
        "recommendation": "400A+ service or engineered review recommended.",
    }


def calculate_residential_load(
    square_feet=0,
    small_appliance_circuits=2,
    laundry_circuits=1,
    range_watts=0,
    dryer_watts=0,
    dishwasher_watts=0,
    disposal_watts=0,
    microwave_watts=0,
    water_heater_watts=0,
    cooling_amps=0,
    heating_amps=0,
    heat_pump_amps=0,
    ev_charger_amps=0,
    pool_amps=0,
    spa_amps=0,
    other_watts=0,
    existing_service_amps=0,
    requested_service_amps=0,
):
    """
    JARVIS Residential Load Calculator.

    This is a contractor estimating / pre-check tool.
    It is not a stamped engineering calculation and should be verified
    against applicable NEC, AHJ, utility, and permit requirements.
    """

    square_feet = D(str(square_feet or 0))
    small_appliance_circuits = D(str(small_appliance_circuits or 0))
    laundry_circuits = D(str(laundry_circuits or 0))

    general_lighting = residential_general_lighting_load(square_feet)
    small_appliance = small_appliance_circuits * D("1500")
    laundry = laundry_circuits * D("1500")

    general_base = general_lighting + small_appliance + laundry
    demanded_general = apply_standard_dwelling_demand(general_base)

    fixed_appliances = appliance_demand([
        dishwasher_watts,
        disposal_watts,
        microwave_watts,
        water_heater_watts,
    ])

    range_load = range_demand(range_watts)
    dryer_load = dryer_demand(dryer_watts)

    hvac_load = largest_hvac_load(
        cooling_watts=amps_to_watts(cooling_amps, 240),
        heating_watts=amps_to_watts(heating_amps, 240),
        heat_pump_watts=amps_to_watts(heat_pump_amps, 240),
    )

    ev_load = amps_to_watts(ev_charger_amps, 240)
    pool_load = amps_to_watts(pool_amps, 240)
    spa_load = amps_to_watts(spa_amps, 240)

    other_load = D(str(other_watts or 0))

    total_watts = (
        demanded_general
        + fixed_appliances
        + range_load
        + dryer_load
        + hvac_load
        + ev_load
        + pool_load
        + spa_load
        + other_load
    )

    calculated_amps = watts_to_amps(total_watts, 240)
    recommendation = service_recommendation(calculated_amps)

    warnings = []

    existing_service_amps = D(str(existing_service_amps or 0))
    requested_service_amps = D(str(requested_service_amps or 0))

    if existing_service_amps and calculated_amps > existing_service_amps:
        warnings.append(
            f"Calculated load appears to exceed existing {existing_service_amps}A service."
        )

    if requested_service_amps and calculated_amps > requested_service_amps:
        warnings.append(
            f"Calculated load appears to exceed requested {requested_service_amps}A service."
        )

    if ev_charger_amps:
        warnings.append(
            "EV charger included. Verify load calculation, charger settings, and available panel capacity."
        )

    if pool_amps or spa_amps:
        warnings.append(
            "Pool/spa load included. Verify GFCI, bonding, disconnect, and equipment nameplate requirements."
        )

    if not cooling_amps and not heating_amps and not heat_pump_amps:
        warnings.append(
            "No HVAC load entered. Load calculation may be incomplete."
        )

    if square_feet <= 0:
        warnings.append(
            "No square footage entered. General lighting load may be incomplete."
        )

    notes = [
        "This is a JARVIS estimating pre-check, not a stamped engineering calculation.",
        "Verify final calculation with NEC, local AHJ, utility requirements, and actual equipment nameplates.",
        "Use actual nameplate ratings when available.",
    ]

    return {
        "inputs": {
            "square_feet": str(square_feet),
            "small_appliance_circuits": str(small_appliance_circuits),
            "laundry_circuits": str(laundry_circuits),
            "existing_service_amps": str(existing_service_amps),
            "requested_service_amps": str(requested_service_amps),
        },
        "loads_watts": {
            "general_lighting": money(general_lighting),
            "small_appliance": money(small_appliance),
            "laundry": money(laundry),
            "general_base": money(general_base),
            "demanded_general": money(demanded_general),
            "fixed_appliances": money(fixed_appliances),
            "range": money(range_load),
            "dryer": money(dryer_load),
            "hvac": money(hvac_load),
            "ev_charger": money(ev_load),
            "pool": money(pool_load),
            "spa": money(spa_load),
            "other": money(other_load),
            "total": money(total_watts),
        },
        "calculated_amps": calculated_amps,
        "recommended_service_amps": recommendation["recommended_service_amps"],
        "recommendation": recommendation["recommendation"],
        "warnings": warnings,
        "notes": notes,
    }


def format_load_calculation(result):
    lines = []

    lines.append("JARVIS Load Calculation")
    lines.append("")
    lines.append(f"Calculated Load: {result['calculated_amps']}A")
    lines.append(f"Recommended Service: {result['recommended_service_amps']}A")
    lines.append(result["recommendation"])
    lines.append("")

    lines.append("Load Breakdown:")
    for label, value in result["loads_watts"].items():
        lines.append(f"- {label.replace('_', ' ').title()}: {value}W")

    if result["warnings"]:
        lines.append("")
        lines.append("Warnings / Checks:")
        for warning in result["warnings"]:
            lines.append(f"- {warning}")

    if result["notes"]:
        lines.append("")
        lines.append("Notes:")
        for note in result["notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines)