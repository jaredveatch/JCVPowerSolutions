from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import MaterialCatalog


D = Decimal


def has_field(model, field_name):
    return any(f.name == field_name for f in model._meta.fields)


# JCV Pricebook V2
# Exact-match material pricing for the 306 active MaterialCatalog items.
# This is material pricing only. Labor belongs in ServiceTemplate/labor engine.
JCV_PRICEBOOK = {
    "#10 THHN Copper Black": {"unit_cost": D("0.45"), "sell_price": D("1.00")},
    "#10 THHN Copper Green": {"unit_cost": D("0.45"), "sell_price": D("1.00")},
    "#10 THHN Copper White": {"unit_cost": D("0.45"), "sell_price": D("1.00")},
    "#12 THHN Copper Black": {"unit_cost": D("0.28"), "sell_price": D("0.75")},
    "#12 THHN Copper Green": {"unit_cost": D("0.28"), "sell_price": D("0.75")},
    "#12 THHN Copper White": {"unit_cost": D("0.28"), "sell_price": D("0.75")},
    "#14 THHN Copper Black": {"unit_cost": D("0.18"), "sell_price": D("0.50")},
    "#14 THHN Copper Green": {"unit_cost": D("0.18"), "sell_price": D("0.50")},
    "#14 THHN Copper White": {"unit_cost": D("0.18"), "sell_price": D("0.50")},
    "#2 Aluminum XHHW Conductor": {"unit_cost": D("1.55"), "sell_price": D("4.00")},
    "#2 Bare Copper Ground Wire": {"unit_cost": D("4.15"), "sell_price": D("10.00")},
    "#4 Aluminum XHHW Conductor": {"unit_cost": D("1.05"), "sell_price": D("2.50")},
    "#4 Bare Copper Ground Wire": {"unit_cost": D("2.45"), "sell_price": D("6.00")},
    "#6 Bare Copper Ground Wire": {"unit_cost": D("1.35"), "sell_price": D("3.50")},
    "#6 THHN Copper Black": {"unit_cost": D("1.55"), "sell_price": D("3.50")},
    "#6 THHN Copper Green": {"unit_cost": D("1.55"), "sell_price": D("3.50")},
    "#6 THHN Copper White": {"unit_cost": D("1.55"), "sell_price": D("3.50")},
    "#8 THHN Copper Black": {"unit_cost": D("0.95"), "sell_price": D("2.00")},
    "#8 THHN Copper Green": {"unit_cost": D("0.95"), "sell_price": D("2.00")},
    "#8 THHN Copper White": {"unit_cost": D("0.95"), "sell_price": D("2.00")},

    "1 Inch EMT Conduit": {"unit_cost": D("13.00"), "sell_price": D("29.00")},
    "1 Inch EMT Connector": {"unit_cost": D("1.85"), "sell_price": D("5.50")},
    "1 Inch EMT Coupling": {"unit_cost": D("1.75"), "sell_price": D("5.50")},
    "1 Inch Liquidtight Flexible Conduit": {"unit_cost": D("32.00"), "sell_price": D("68.00")},
    "1 Inch PVC Conduit Schedule 40": {"unit_cost": D("9.50"), "sell_price": D("22.00")},
    "1 Inch PVC Coupling": {"unit_cost": D("1.50"), "sell_price": D("4.50")},
    "1 Inch PVC LB": {"unit_cost": D("10.00"), "sell_price": D("30.00")},
    "1 Inch PVC Male Adapter": {"unit_cost": D("1.65"), "sell_price": D("5.00")},
    "1-1/2 Inch PVC Conduit Schedule 40": {"unit_cost": D("21.00"), "sell_price": D("44.00")},
    "1-1/4 Inch EMT Conduit": {"unit_cost": D("22.00"), "sell_price": D("45.00")},
    "1-1/4 Inch PVC Conduit Schedule 40": {"unit_cost": D("15.00"), "sell_price": D("32.00")},
    "1-Gang Decora Plate": {"unit_cost": D("0.85"), "sell_price": D("3.00")},
    "1-Gang Plastic Nail-On Box": {"unit_cost": D("1.25"), "sell_price": D("4.00")},
    "1-Gang Toggle Plate": {"unit_cost": D("0.85"), "sell_price": D("3.00")},
    "1/2 EMT Conduit": {"unit_cost": D("5.50"), "sell_price": D("13.00")},
    "1/2 EMT Connector": {"unit_cost": D("0.75"), "sell_price": D("2.50")},
    "1/2 EMT Coupling": {"unit_cost": D("0.70"), "sell_price": D("2.00")},
    "1/2 Inch Snap-In Bushing": {"unit_cost": D("0.45"), "sell_price": D("1.25")},
    "1/2 Liquidtight Connector 90 Degree": {"unit_cost": D("7.50"), "sell_price": D("23.00")},
    "1/2 Liquidtight Connector Straight": {"unit_cost": D("5.50"), "sell_price": D("17.00")},
    "1/2 Liquidtight Flexible Conduit": {"unit_cost": D("17.00"), "sell_price": D("38.00")},
    "1/2 PVC Conduit Schedule 40": {"unit_cost": D("4.25"), "sell_price": D("10.00")},
    "1/2 PVC Coupling": {"unit_cost": D("0.75"), "sell_price": D("2.50")},
    "1/2 PVC LB": {"unit_cost": D("5.50"), "sell_price": D("17.00")},
    "1/2 PVC Male Adapter": {"unit_cost": D("0.85"), "sell_price": D("2.50")},

    "10/2 NM-B Cable": {"unit_cost": D("2.10"), "sell_price": D("4.00")},
    "10/3 NM-B Cable": {"unit_cost": D("3.40"), "sell_price": D("6.50")},
    "12/2 NM-B Cable": {"unit_cost": D("0.95"), "sell_price": D("1.75")},
    "12/3 NM-B Cable": {"unit_cost": D("1.35"), "sell_price": D("2.50")},
    "14/2 Landscape Lighting Cable": {"unit_cost": D("0.55"), "sell_price": D("1.00")},
    "14/2 NM-B Cable": {"unit_cost": D("0.55"), "sell_price": D("1.00")},
    "14/3 NM-B Cable": {"unit_cost": D("0.85"), "sell_price": D("1.50")},
    "15A Decora Receptacle": {"unit_cost": D("3.50"), "sell_price": D("11.00")},
    "15A Duplex Receptacle": {"unit_cost": D("2.25"), "sell_price": D("8.00")},
    "15A Tamper Resistant Receptacle": {"unit_cost": D("3.00"), "sell_price": D("10.00")},
    "16/2 Landscape Lighting Cable": {"unit_cost": D("0.42"), "sell_price": D("0.75")},
    "18/2 Thermostat Wire": {"unit_cost": D("0.28"), "sell_price": D("0.75")},
    "18/5 Thermostat Wire": {"unit_cost": D("0.55"), "sell_price": D("1.50")},
    "2 Inch PVC Conduit Schedule 40": {"unit_cost": D("34.00"), "sell_price": D("68.00")},
    "2 Inch Rigid Bushing": {"unit_cost": D("3.50"), "sell_price": D("11.00")},
    "2 Inch Rigid Locknut": {"unit_cost": D("1.25"), "sell_price": D("4.00")},
    "2 Inch Rigid Service Mast": {"unit_cost": D("55.00"), "sell_price": D("110.00")},
    "2 Inch Service Entrance Strap": {"unit_cost": D("5.00"), "sell_price": D("15.00")},
    "2 Inch Weatherhead": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "2-Gang Decora Plate": {"unit_cost": D("1.50"), "sell_price": D("5.50")},
    "2-Gang Plastic Nail-On Box": {"unit_cost": D("2.50"), "sell_price": D("7.00")},
    "2-Gang Toggle Plate": {"unit_cost": D("1.50"), "sell_price": D("5.50")},
    "2/0 Aluminum XHHW Conductor": {"unit_cost": D("2.85"), "sell_price": D("7.00")},
    "2/3 SER Feeder Cable": {"unit_cost": D("4.25"), "sell_price": D("7.50")},
    "200A Meter Main Combination": {"unit_cost": D("425.00"), "sell_price": D("638.00")},
    "200A Meter Socket Ring Type": {"unit_cost": D("145.00"), "sell_price": D("254.00")},
    "200A Meter Socket Ringless": {"unit_cost": D("165.00"), "sell_price": D("289.00")},
    "200A Service Mast Kit": {"unit_cost": D("140.00"), "sell_price": D("245.00")},
    "20A Decora Receptacle": {"unit_cost": D("4.50"), "sell_price": D("14.00")},
    "20A Duplex Receptacle": {"unit_cost": D("3.25"), "sell_price": D("10.00")},
    "20A Tamper Resistant Receptacle": {"unit_cost": D("4.00"), "sell_price": D("12.00")},

    "3-Gang Decora Plate": {"unit_cost": D("2.50"), "sell_price": D("9.00")},
    "3-Gang Plastic Nail-On Box": {"unit_cost": D("4.25"), "sell_price": D("11.00")},
    "3-Way Switch": {"unit_cost": D("4.50"), "sell_price": D("14.00")},
    "3/4 EMT Conduit": {"unit_cost": D("8.50"), "sell_price": D("19.00")},
    "3/4 EMT Connector": {"unit_cost": D("1.10"), "sell_price": D("3.50")},
    "3/4 EMT Coupling": {"unit_cost": D("1.00"), "sell_price": D("3.00")},
    "3/4 Liquidtight Connector 90 Degree": {"unit_cost": D("10.50"), "sell_price": D("32.00")},
    "3/4 Liquidtight Connector Straight": {"unit_cost": D("7.50"), "sell_price": D("23.00")},
    "3/4 Liquidtight Flexible Conduit": {"unit_cost": D("23.00"), "sell_price": D("50.00")},
    "3/4 PVC Conduit Schedule 40": {"unit_cost": D("6.00"), "sell_price": D("14.00")},
    "3/4 PVC Coupling": {"unit_cost": D("1.00"), "sell_price": D("3.00")},
    "3/4 PVC LB": {"unit_cost": D("7.50"), "sell_price": D("23.00")},
    "3/4 PVC Male Adapter": {"unit_cost": D("1.10"), "sell_price": D("3.50")},

    "4 Inch LED Recessed Wafer Light": {"unit_cost": D("18.00"), "sell_price": D("38.00")},
    "4 Inch Octagon Box": {"unit_cost": D("2.50"), "sell_price": D("8.00")},
    "4 Inch Round Blank Cover": {"unit_cost": D("1.25"), "sell_price": D("5.00")},
    "4 Inch Round Ceiling Box": {"unit_cost": D("2.50"), "sell_price": D("8.00")},
    "4 Inch Square Blank Cover": {"unit_cost": D("1.25"), "sell_price": D("5.00")},
    "4 Inch Square Metal Box": {"unit_cost": D("3.00"), "sell_price": D("9.00")},
    "4-11/16 Inch Square Metal Box": {"unit_cost": D("5.50"), "sell_price": D("15.00")},
    "4-Gang Decora Plate": {"unit_cost": D("4.00"), "sell_price": D("14.00")},
    "4-Gang Mud Ring": {"unit_cost": D("4.25"), "sell_price": D("13.00")},
    "4-Gang Plastic Nail-On Box": {"unit_cost": D("6.25"), "sell_price": D("15.00")},
    "4-Way Switch": {"unit_cost": D("8.50"), "sell_price": D("24.00")},
    "4/0 Aluminum XHHW Conductor": {"unit_cost": D("4.35"), "sell_price": D("11.00")},
    "4/3 SER Feeder Cable": {"unit_cost": D("3.25"), "sell_price": D("5.50")},

    "50A Spa Panel": {"unit_cost": D("115.00"), "sell_price": D("225.00")},
    "6 Inch LED Recessed Wafer Light": {"unit_cost": D("20.00"), "sell_price": D("42.00")},
    "6 Inch LED Trim Kit": {"unit_cost": D("12.00"), "sell_price": D("28.00")},
    "6 Inch Recessed Can Housing": {"unit_cost": D("16.00"), "sell_price": D("36.00")},
    "6/3 NM-B Cable": {"unit_cost": D("8.50"), "sell_price": D("16.00")},
    "60A Spa Panel": {"unit_cost": D("140.00"), "sell_price": D("265.00")},
    "8 ft Ground Rod": {"unit_cost": D("18.00"), "sell_price": D("38.00")},
    "8/3 NM-B Cable": {"unit_cost": D("5.75"), "sell_price": D("11.00")},

    "AC Disconnect 60A Fused": {"unit_cost": D("24.00"), "sell_price": D("60.00")},
    "AC Disconnect 60A Non-Fused": {"unit_cost": D("14.00"), "sell_price": D("40.00")},
    "AFCI/GFCI Receptacle": {"unit_cost": D("24.00"), "sell_price": D("58.00")},
    "Adjustable Fan Brace Box": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Anti-Ox Compound": {"unit_cost": D("8.00"), "sell_price": D("22.00")},
    "Bathroom Exhaust Fan": {"unit_cost": D("75.00"), "sell_price": D("135.00")},
    "Blank Cover Plate": {"unit_cost": D("1.25"), "sell_price": D("4.50")},
    "Blue Wire Nuts": {"unit_cost": D("0.12"), "sell_price": D("0.75")},
    "Bonding Bushing 1 Inch": {"unit_cost": D("8.50"), "sell_price": D("26.00")},
    "Bonding Bushing 1-1/2 Inch": {"unit_cost": D("14.00"), "sell_price": D("42.00")},
    "Bonding Bushing 1-1/4 Inch": {"unit_cost": D("12.00"), "sell_price": D("36.00")},
    "Bonding Bushing 2 Inch": {"unit_cost": D("18.00"), "sell_price": D("54.00")},
    "Cat6 Cable": {"unit_cost": D("0.35"), "sell_price": D("1.00")},
    "Ceiling Fan": {"unit_cost": D("95.00"), "sell_price": D("157.00")},
    "Ceiling Fan Rated Box": {"unit_cost": D("16.00"), "sell_price": D("40.00")},
    "Ceiling Light Fixture": {"unit_cost": D("45.00"), "sell_price": D("83.00")},
    "Chandelier": {"unit_cost": D("125.00"), "sell_price": D("220.00")},
    "ChargePoint Home Flex": {"unit_cost": D("600.00"), "sell_price": D("899.00")},
    "Coax Cable RG6": {"unit_cost": D("0.32"), "sell_price": D("0.75")},
    "Data Wall Plate": {"unit_cost": D("4.00"), "sell_price": D("14.00")},
    "Decora 3-Way Switch": {"unit_cost": D("5.50"), "sell_price": D("16.00")},
    "Decora Single Pole Switch": {"unit_cost": D("3.25"), "sell_price": D("10.00")},
    "Dimmer Switch": {"unit_cost": D("18.00"), "sell_price": D("43.00")},
    "Dishwasher Cord Kit": {"unit_cost": D("12.00"), "sell_price": D("28.00")},
    "Doorbell Chime": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Doorbell Transformer": {"unit_cost": D("16.00"), "sell_price": D("40.00")},
    "Dryer Receptacle 30A": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Duct Seal": {"unit_cost": D("5.00"), "sell_price": D("15.00")},
    "Duplex Receptacle Plate": {"unit_cost": D("0.85"), "sell_price": D("3.00")},
    "EV Pedestal Mount": {"unit_cost": D("185.00"), "sell_price": D("325.00")},
    "Ecobee Thermostat": {"unit_cost": D("185.00"), "sell_price": D("300.00")},
    "Electrical Tape": {"unit_cost": D("4.00"), "sell_price": D("11.00")},
    "Emporia EV Charger": {"unit_cost": D("400.00"), "sell_price": D("650.00")},
    "Equipotential Bonding Clamp": {"unit_cost": D("12.00"), "sell_price": D("35.00")},
    "Exterior Bell Box": {"unit_cost": D("8.50"), "sell_price": D("24.00")},
    "FS Box Double Gang": {"unit_cost": D("12.00"), "sell_price": D("32.00")},
    "FS Box Single Gang": {"unit_cost": D("8.00"), "sell_price": D("22.00")},
    "Fire Caulk": {"unit_cost": D("12.00"), "sell_price": D("30.00")},
    "Flood Light": {"unit_cost": D("38.00"), "sell_price": D("76.00")},
    "GFCI Receptacle": {"unit_cost": D("14.00"), "sell_price": D("37.00")},
    "Garbage Disposal Switch Kit": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Generator Inlet 30A": {"unit_cost": D("45.00"), "sell_price": D("100.00")},
    "Generator Inlet 50A": {"unit_cost": D("65.00"), "sell_price": D("145.00")},
    "Generator Power Cord 30A": {"unit_cost": D("80.00"), "sell_price": D("160.00")},
    "Generator Power Cord 50A": {"unit_cost": D("135.00"), "sell_price": D("250.00")},
    "Generator Surge Protector": {"unit_cost": D("95.00"), "sell_price": D("190.00")},
    "Ground Rod Clamp": {"unit_cost": D("3.50"), "sell_price": D("12.00")},
    "Ground Screws": {"unit_cost": D("0.10"), "sell_price": D("0.50")},
    "Intersystem Bonding Bridge": {"unit_cost": D("12.00"), "sell_price": D("30.00")},
    "Keystone Jack Cat6": {"unit_cost": D("4.50"), "sell_price": D("14.00")},
    "Landscape Stake Light": {"unit_cost": D("22.00"), "sell_price": D("50.00")},
    "Landscape Transformer": {"unit_cost": D("85.00"), "sell_price": D("160.00")},
    "Leviton Smart Switch": {"unit_cost": D("32.00"), "sell_price": D("67.00")},
    "Load Management Device": {"unit_cost": D("750.00"), "sell_price": D("1199.00")},
    "Lutron Caseta Dimmer": {"unit_cost": D("65.00"), "sell_price": D("120.00")},
    "Lutron Caseta Pico Remote": {"unit_cost": D("22.00"), "sell_price": D("45.00")},
    "Lutron Smart Bridge": {"unit_cost": D("80.00"), "sell_price": D("145.00")},
    "MC Cable Connector": {"unit_cost": D("1.25"), "sell_price": D("4.00")},
    "Masonry Anchors": {"unit_cost": D("0.35"), "sell_price": D("1.50")},
    "Metal Switch Box": {"unit_cost": D("2.25"), "sell_price": D("7.00")},
    "Mini Split Disconnect": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Mini Split Surge Protector": {"unit_cost": D("95.00"), "sell_price": D("190.00")},
    "Mini Split Whip": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "NEMA 14-50 EV Receptacle": {"unit_cost": D("42.00"), "sell_price": D("91.00")},
    "NM Cable Staples": {"unit_cost": D("0.08"), "sell_price": D("0.50")},
    "Nest Thermostat": {"unit_cost": D("145.00"), "sell_price": D("240.00")},
    "Occupancy Sensor Switch": {"unit_cost": D("24.00"), "sell_price": D("55.00")},
    "Old Work 1-Gang Box": {"unit_cost": D("2.75"), "sell_price": D("8.00")},
    "Old Work 2-Gang Box": {"unit_cost": D("4.50"), "sell_price": D("13.00")},
    "Old Work 3-Gang Box": {"unit_cost": D("8.00"), "sell_price": D("20.00")},
    "Old Work 4-Gang Box": {"unit_cost": D("12.00"), "sell_price": D("30.00")},
    "Oversized Decora Plate": {"unit_cost": D("1.65"), "sell_price": D("6.00")},
    "Photocell": {"unit_cost": D("9.00"), "sell_price": D("25.00")},
    "Pool Disconnect": {"unit_cost": D("24.00"), "sell_price": D("60.00")},
    "Pool Timer": {"unit_cost": D("65.00"), "sell_price": D("130.00")},
    "Post Light Fixture": {"unit_cost": D("55.00"), "sell_price": D("100.00")},
    "Protective Nail Plate": {"unit_cost": D("0.75"), "sell_price": D("3.00")},
    "Range Receptacle 50A": {"unit_cost": D("22.00"), "sell_price": D("55.00")},
    "Red Wire Nuts": {"unit_cost": D("0.12"), "sell_price": D("0.75")},
    "Ring Doorbell": {"unit_cost": D("100.00"), "sell_price": D("180.00")},
    "Romex Connector": {"unit_cost": D("0.85"), "sell_price": D("2.50")},
    "Self-Tapping Screws": {"unit_cost": D("0.10"), "sell_price": D("0.50")},
    "Service Entrance Cable #2 Aluminum SER": {"unit_cost": D("4.25"), "sell_price": D("7.50")},
    "Service Entrance Cable #4 Aluminum SER": {"unit_cost": D("3.25"), "sell_price": D("5.50")},
    "Service Entrance Cable 2/0 Aluminum SER": {"unit_cost": D("7.25"), "sell_price": D("13.00")},
    "Service Entrance Cable 4/0 Aluminum SER": {"unit_cost": D("11.50"), "sell_price": D("20.00")},
    "Single Gang Mud Ring": {"unit_cost": D("1.35"), "sell_price": D("5.00")},
    "Single Pole Switch": {"unit_cost": D("2.25"), "sell_price": D("8.00")},
    "Smart Switch": {"unit_cost": D("32.00"), "sell_price": D("67.00")},
    "Smoke Detector Hardwired": {"unit_cost": D("22.00"), "sell_price": D("50.00")},
    "Smoke Detector Remodel Box": {"unit_cost": D("4.50"), "sell_price": D("13.00")},
    "Smoke/CO Detector Hardwired": {"unit_cost": D("24.00"), "sell_price": D("54.00")},
    "Spa Disconnect GFCI": {"unit_cost": D("125.00"), "sell_price": D("240.00")},

    "Square D Homeline 100A Indoor Main Breaker Panel 20/40": {"unit_cost": D("165.00"), "sell_price": D("289.00")},
    "Square D Homeline 100A Main Breaker": {"unit_cost": D("85.00"), "sell_price": D("165.00")},
    "Square D Homeline 100A Main Lug Subpanel 12/24 Indoor": {"unit_cost": D("95.00"), "sell_price": D("185.00")},
    "Square D Homeline 100A Main Lug Subpanel 6/12 Indoor": {"unit_cost": D("70.00"), "sell_price": D("140.00")},
    "Square D Homeline 100A Mobile Home Outdoor Feed Through": {"unit_cost": D("245.00"), "sell_price": D("425.00")},
    "Square D Homeline 100A Outdoor Main Breaker Panel 20/40": {"unit_cost": D("210.00"), "sell_price": D("365.00")},
    "Square D Homeline 100A Outdoor Main Lug Subpanel": {"unit_cost": D("130.00"), "sell_price": D("225.00")},
    "Square D Homeline 100A Two Pole Breaker": {"unit_cost": D("65.00"), "sell_price": D("125.00")},

    "Square D Homeline 125A Indoor Main Breaker Panel 24/48": {"unit_cost": D("195.00"), "sell_price": D("335.00")},
    "Square D Homeline 125A Indoor Main Breaker Panel 30/60": {"unit_cost": D("225.00"), "sell_price": D("385.00")},
    "Square D Homeline 125A Main Breaker": {"unit_cost": D("95.00"), "sell_price": D("180.00")},
    "Square D Homeline 125A Main Lug Subpanel 12/24 Indoor": {"unit_cost": D("105.00"), "sell_price": D("195.00")},
    "Square D Homeline 125A Main Lug Subpanel 20/40 Indoor": {"unit_cost": D("145.00"), "sell_price": D("255.00")},
    "Square D Homeline 125A Mobile Home Outdoor Feed Through": {"unit_cost": D("265.00"), "sell_price": D("450.00")},
    "Square D Homeline 125A Outdoor Main Breaker Panel 24/48": {"unit_cost": D("240.00"), "sell_price": D("410.00")},
    "Square D Homeline 125A Outdoor Main Breaker Panel 30/60": {"unit_cost": D("270.00"), "sell_price": D("460.00")},
    "Square D Homeline 125A Outdoor Main Lug Subpanel": {"unit_cost": D("150.00"), "sell_price": D("260.00")},
    "Square D Homeline 125A Two Pole Breaker": {"unit_cost": D("85.00"), "sell_price": D("160.00")},

    "Square D Homeline 150A Indoor Main Breaker Panel 30/60": {"unit_cost": D("245.00"), "sell_price": D("415.00")},
    "Square D Homeline 150A Indoor Main Breaker Panel 40/80": {"unit_cost": D("285.00"), "sell_price": D("475.00")},
    "Square D Homeline 150A Main Breaker": {"unit_cost": D("125.00"), "sell_price": D("225.00")},
    "Square D Homeline 150A Outdoor Main Breaker Panel 30/60": {"unit_cost": D("295.00"), "sell_price": D("500.00")},
    "Square D Homeline 150A Outdoor Main Breaker Panel 40/80": {"unit_cost": D("335.00"), "sell_price": D("565.00")},

    "Square D Homeline 15A CAFI Breaker": {"unit_cost": D("48.00"), "sell_price": D("100.00")},
    "Square D Homeline 15A Dual Function Breaker": {"unit_cost": D("62.00"), "sell_price": D("124.00")},
    "Square D Homeline 15A GFCI Breaker": {"unit_cost": D("58.00"), "sell_price": D("116.00")},
    "Square D Homeline 15A Single Pole Breaker": {"unit_cost": D("7.50"), "sell_price": D("19.00")},
    "Square D Homeline 15A Two Pole Breaker": {"unit_cost": D("18.00"), "sell_price": D("42.00")},

    "Square D Homeline 200A Indoor Main Breaker Panel 30/60": {"unit_cost": D("285.00"), "sell_price": D("475.00")},
    "Square D Homeline 200A Indoor Main Breaker Panel 40/80": {"unit_cost": D("325.00"), "sell_price": D("535.00")},
    "Square D Homeline 200A Indoor Main Breaker Panel 42/84": {"unit_cost": D("365.00"), "sell_price": D("595.00")},
    "Square D Homeline 200A Main Breaker": {"unit_cost": D("150.00"), "sell_price": D("270.00")},
    "Square D Homeline 200A Main Lug Subpanel 30/60 Indoor": {"unit_cost": D("185.00"), "sell_price": D("325.00")},
    "Square D Homeline 200A Main Lug Subpanel 40/80 Indoor": {"unit_cost": D("225.00"), "sell_price": D("385.00")},
    "Square D Homeline 200A Main Lug Subpanel 42/84 Indoor": {"unit_cost": D("245.00"), "sell_price": D("425.00")},
    "Square D Homeline 200A Mobile Home Outdoor Panel Feed Through": {"unit_cost": D("360.00"), "sell_price": D("625.00")},
    "Square D Homeline 200A Outdoor Main Breaker Panel 30/60": {"unit_cost": D("345.00"), "sell_price": D("575.00")},
    "Square D Homeline 200A Outdoor Main Breaker Panel 40/80": {"unit_cost": D("385.00"), "sell_price": D("650.00")},
    "Square D Homeline 200A Outdoor Main Breaker Panel 42/84": {"unit_cost": D("425.00"), "sell_price": D("700.00")},
    "Square D Homeline 200A Outdoor Main Lug Subpanel": {"unit_cost": D("275.00"), "sell_price": D("475.00")},

    "Square D Homeline 20A CAFI Breaker": {"unit_cost": D("48.00"), "sell_price": D("100.00")},
    "Square D Homeline 20A Dual Function Breaker": {"unit_cost": D("62.00"), "sell_price": D("124.00")},
    "Square D Homeline 20A GFCI Breaker": {"unit_cost": D("58.00"), "sell_price": D("116.00")},
    "Square D Homeline 20A Single Pole Breaker": {"unit_cost": D("8.00"), "sell_price": D("20.00")},
    "Square D Homeline 20A Two Pole Breaker": {"unit_cost": D("18.00"), "sell_price": D("42.00")},

    "Square D Homeline 225A Indoor Main Breaker Panel 42/84": {"unit_cost": D("395.00"), "sell_price": D("650.00")},
    "Square D Homeline 225A Indoor Main Breaker Panel 54/108": {"unit_cost": D("475.00"), "sell_price": D("775.00")},
    "Square D Homeline 225A Main Breaker": {"unit_cost": D("175.00"), "sell_price": D("310.00")},
    "Square D Homeline 225A Outdoor Main Breaker Panel 42/84": {"unit_cost": D("475.00"), "sell_price": D("775.00")},

    "Square D Homeline 25A Single Pole Breaker": {"unit_cost": D("11.00"), "sell_price": D("28.00")},
    "Square D Homeline 25A Two Pole Breaker": {"unit_cost": D("20.00"), "sell_price": D("45.00")},
    "Square D Homeline 30A 2P GFCI Breaker": {"unit_cost": D("95.00"), "sell_price": D("180.00")},
    "Square D Homeline 30A Single Pole Breaker": {"unit_cost": D("12.00"), "sell_price": D("30.00")},
    "Square D Homeline 30A Two Pole Breaker": {"unit_cost": D("22.00"), "sell_price": D("50.00")},
    "Square D Homeline 35A Two Pole Breaker": {"unit_cost": D("24.00"), "sell_price": D("55.00")},
    "Square D Homeline 40A 2P GFCI Breaker": {"unit_cost": D("105.00"), "sell_price": D("195.00")},
    "Square D Homeline 40A Two Pole Breaker": {"unit_cost": D("24.00"), "sell_price": D("55.00")},
    "Square D Homeline 45A Two Pole Breaker": {"unit_cost": D("26.00"), "sell_price": D("60.00")},
    "Square D Homeline 50A 2P GFCI Breaker": {"unit_cost": D("115.00"), "sell_price": D("215.00")},
    "Square D Homeline 50A Two Pole Breaker": {"unit_cost": D("28.00"), "sell_price": D("65.00")},
    "Square D Homeline 60A 2P GFCI Breaker": {"unit_cost": D("125.00"), "sell_price": D("235.00")},
    "Square D Homeline 60A Main Lug Subpanel 2/4 Indoor": {"unit_cost": D("55.00"), "sell_price": D("120.00")},
    "Square D Homeline 60A Two Pole Breaker": {"unit_cost": D("32.00"), "sell_price": D("75.00")},
    "Square D Homeline 70A Main Lug Subpanel 4/8 Indoor": {"unit_cost": D("65.00"), "sell_price": D("135.00")},
    "Square D Homeline 70A Two Pole Breaker": {"unit_cost": D("45.00"), "sell_price": D("95.00")},
    "Square D Homeline 80A Two Pole Breaker": {"unit_cost": D("55.00"), "sell_price": D("110.00")},
    "Square D Homeline 90A Two Pole Breaker": {"unit_cost": D("60.00"), "sell_price": D("120.00")},

    "Square D Homeline Filler Plates": {"unit_cost": D("3.50"), "sell_price": D("12.00")},
    "Square D Homeline Generator Interlock Kit 100-125A Indoor": {"unit_cost": D("75.00"), "sell_price": D("150.00")},
    "Square D Homeline Generator Interlock Kit 150-225A Indoor": {"unit_cost": D("85.00"), "sell_price": D("165.00")},
    "Square D Homeline Generator Ready Panel 100A": {"unit_cost": D("315.00"), "sell_price": D("525.00")},
    "Square D Homeline Generator Ready Panel 200A": {"unit_cost": D("450.00"), "sell_price": D("725.00")},
    "Square D Homeline Ground Bar Kit": {"unit_cost": D("8.00"), "sell_price": D("18.00")},
    "Square D Homeline Indoor Flush Cover": {"unit_cost": D("65.00"), "sell_price": D("125.00")},
    "Square D Homeline Indoor Surface Cover": {"unit_cost": D("65.00"), "sell_price": D("125.00")},
    "Square D Homeline Neutral Lug Kit": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Square D Homeline Outdoor Cover": {"unit_cost": D("85.00"), "sell_price": D("160.00")},
    "Square D Homeline Quad 20/30A Breaker": {"unit_cost": D("38.00"), "sell_price": D("80.00")},
    "Square D Homeline Quad 20/50A Breaker": {"unit_cost": D("42.00"), "sell_price": D("88.00")},
    "Square D Homeline Quad 30/50A Breaker": {"unit_cost": D("45.00"), "sell_price": D("95.00")},
    "Square D Homeline Tandem 15/15A Breaker": {"unit_cost": D("18.00"), "sell_price": D("41.00")},
    "Square D Homeline Tandem 15/20A Breaker": {"unit_cost": D("18.00"), "sell_price": D("41.00")},
    "Square D Homeline Tandem 20/20A Breaker": {"unit_cost": D("18.00"), "sell_price": D("41.00")},
    "Square D Homeline Whole Home Surge Protector": {"unit_cost": D("95.00"), "sell_price": D("190.00")},

    "Tesla Wall Connector": {"unit_cost": D("450.00"), "sell_price": D("725.00")},
    "Timer Switch": {"unit_cost": D("22.00"), "sell_price": D("50.00")},
    "Two Gang Mud Ring": {"unit_cost": D("2.50"), "sell_price": D("8.00")},
    "Type 2 SPD 140kA": {"unit_cost": D("185.00"), "sell_price": D("325.00")},
    "Type 2 SPD 80kA": {"unit_cost": D("95.00"), "sell_price": D("190.00")},
    "USB Receptacle": {"unit_cost": D("18.00"), "sell_price": D("43.00")},
    "Vanity Light": {"unit_cost": D("65.00"), "sell_price": D("114.00")},
    "Wago 2-Port Lever Connector": {"unit_cost": D("0.65"), "sell_price": D("2.50")},
    "Wago 3-Port Lever Connector": {"unit_cost": D("0.75"), "sell_price": D("3.00")},
    "Water Heater Disconnect": {"unit_cost": D("18.00"), "sell_price": D("45.00")},
    "Water Pipe Ground Clamp": {"unit_cost": D("4.50"), "sell_price": D("14.00")},
    "Weather Resistant GFCI Receptacle": {"unit_cost": D("16.00"), "sell_price": D("40.00")},
    "Weatherproof In-Use Cover": {"unit_cost": D("9.50"), "sell_price": D("26.00")},
    "Weatherproof While-In-Use Extra Duty Cover": {"unit_cost": D("14.00"), "sell_price": D("36.00")},
    "Whip 1/2 Inch 6 ft": {"unit_cost": D("16.00"), "sell_price": D("40.00")},
    "Whip 3/4 Inch 6 ft": {"unit_cost": D("20.00"), "sell_price": D("50.00")},
    "Wiremold Surface Raceway": {"unit_cost": D("18.00"), "sell_price": D("42.00")},
    "Yellow Wire Nuts": {"unit_cost": D("0.12"), "sell_price": D("0.75")},
    "Zip Ties": {"unit_cost": D("0.08"), "sell_price": D("0.50")},
}


class Command(BaseCommand):
    help = "Phase 3B: Apply exact-match JCV Pricebook V2 pricing to MaterialCatalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview pricing without saving changes.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing non-zero unit_cost values.",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Fail if any MaterialCatalog item is missing from JCV_PRICEBOOK.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]
        strict = options["strict"]

        has_sell_price = has_field(MaterialCatalog, "sell_price")
        has_markup = has_field(MaterialCatalog, "markup_multiplier")
        has_notes = has_field(MaterialCatalog, "pricing_notes")

        materials = list(MaterialCatalog.objects.all().order_by("name"))
        db_names = {m.name for m in materials}
        pricebook_names = set(JCV_PRICEBOOK.keys())

        missing_from_pricebook = sorted(db_names - pricebook_names)
        extra_in_pricebook = sorted(pricebook_names - db_names)

        self.stdout.write(self.style.WARNING("JCV exact-match Pricebook V2 started..."))
        self.stdout.write(f"Database materials: {len(db_names)}")
        self.stdout.write(f"Pricebook entries: {len(pricebook_names)}")

        if missing_from_pricebook:
            self.stdout.write(self.style.ERROR(""))
            self.stdout.write(self.style.ERROR("Materials missing from JCV_PRICEBOOK:"))
            for name in missing_from_pricebook:
                self.stdout.write(self.style.ERROR(f"  - {name}"))

        if extra_in_pricebook:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Extra entries in JCV_PRICEBOOK not found in database:"))
            for name in extra_in_pricebook:
                self.stdout.write(self.style.WARNING(f"  - {name}"))

        if strict and missing_from_pricebook:
            self.stdout.write(self.style.ERROR(""))
            self.stdout.write(self.style.ERROR("Strict mode enabled. Aborting before pricing."))
            return

        updated = 0
        skipped_existing = 0
        skipped_missing = 0

        save_fields = ["unit_cost"]
        if has_sell_price:
            save_fields.append("sell_price")
        if has_markup:
            save_fields.append("markup_multiplier")
        if has_notes:
            save_fields.append("pricing_notes")

        with transaction.atomic():
            for material in materials:
                pricing = JCV_PRICEBOOK.get(material.name)

                if not pricing:
                    skipped_missing += 1
                    continue

                current_cost = getattr(material, "unit_cost", None)

                if current_cost and current_cost > 0 and not overwrite:
                    skipped_existing += 1
                    continue

                unit_cost = pricing["unit_cost"]
                sell_price = pricing["sell_price"]

                material.unit_cost = unit_cost

                if has_sell_price:
                    material.sell_price = sell_price

                if has_markup:
                    if unit_cost > 0:
                        material.markup_multiplier = (sell_price / unit_cost).quantize(D("0.01"))
                    else:
                        material.markup_multiplier = D("0.00")

                if has_notes:
                    material.pricing_notes = (
                        "JCV Pricebook V2 exact-match pricing. "
                        f"Material cost: ${unit_cost}. "
                        f"Customer material price: ${sell_price}. "
                        "Labor is priced separately in service templates."
                    )

                updated += 1

                self.stdout.write(
                    f"{material.name} | cost ${unit_cost} | sell ${sell_price}"
                )

                if not dry_run:
                    material.save(update_fields=save_fields)

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("JCV exact-match Pricebook V2 complete."))
        self.stdout.write(f"Updated: {updated}")
        self.stdout.write(f"Skipped existing priced items: {skipped_existing}")
        self.stdout.write(f"Skipped missing pricebook entries: {skipped_missing}")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No database changes saved."))