from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import MaterialCatalog


class Command(BaseCommand):

    help = "Seed residential electrical materials"

    def handle(self, *args, **kwargs):

        materials = [
    # =====================================================
    # SQUARE D HOMELINE PANELS / LOAD CENTERS / ENCLOSURES
    # =====================================================
    ("Square D Homeline 100A Indoor Main Breaker Panel 20/40", "Square D", "HOM2040M100PC", "each", "0.00", "2.50"),
    ("Square D Homeline 125A Indoor Main Breaker Panel 24/48", "Square D", "HOM2448M125PC", "each", "0.00", "2.75"),
    ("Square D Homeline 150A Indoor Main Breaker Panel 30/60", "Square D", "HOM3060M150PC", "each", "0.00", "3.00"),
    ("Square D Homeline 200A Indoor Main Breaker Panel 30/60", "Square D", "HOM3060M200PC", "each", "0.00", "3.25"),
    ("Square D Homeline 200A Indoor Main Breaker Panel 40/80", "Square D", "HOM4080M200PC", "each", "0.00", "3.50"),
    ("Square D Homeline 200A Indoor Main Breaker Panel 42/84", "Square D", "HOM4284M200PC", "each", "0.00", "3.75"),
    ("Square D Homeline 225A Indoor Main Breaker Panel 42/84", "Square D", "HOM4284M225PC", "each", "0.00", "4.00"),

    ("Square D Homeline 100A Outdoor Main Breaker Panel 20/40", "Square D", "HOM2040M100PRB", "each", "0.00", "3.00"),
    ("Square D Homeline 125A Outdoor Main Breaker Panel 24/48", "Square D", "HOM2448M125PRB", "each", "0.00", "3.25"),
    ("Square D Homeline 150A Outdoor Main Breaker Panel 30/60", "Square D", "HOM3060M150PRB", "each", "0.00", "3.50"),
    ("Square D Homeline 200A Outdoor Main Breaker Panel 30/60", "Square D", "HOM3060M200PRB", "each", "0.00", "3.75"),
    ("Square D Homeline 200A Outdoor Main Breaker Panel 40/80", "Square D", "HOM4080M200PRB", "each", "0.00", "4.00"),

    ("Square D Homeline 60A Main Lug Subpanel 2/4 Indoor", "Square D", "HOM24L70SCP", "each", "0.00", "1.25"),
    ("Square D Homeline 100A Main Lug Subpanel 6/12 Indoor", "Square D", "HOM612L100SCP", "each", "0.00", "1.50"),
    ("Square D Homeline 125A Main Lug Subpanel 12/24 Indoor", "Square D", "HOM1224L125PC", "each", "0.00", "2.00"),
    ("Square D Homeline 125A Main Lug Subpanel 20/40 Indoor", "Square D", "HOM2040L125PC", "each", "0.00", "2.25"),
    ("Square D Homeline 200A Main Lug Subpanel 30/60 Indoor", "Square D", "HOM3060L225PC", "each", "0.00", "2.75"),

    ("Square D Homeline 100A Outdoor Main Lug Subpanel", "Square D", "HOM612L100RB", "each", "0.00", "2.00"),
    ("Square D Homeline 125A Outdoor Main Lug Subpanel", "Square D", "HOM1224L125PRB", "each", "0.00", "2.50"),
    ("Square D Homeline 200A Outdoor Main Lug Subpanel", "Square D", "HOM3060L225PRB", "each", "0.00", "3.00"),

    ("Square D Homeline 200A Mobile Home Outdoor Panel Feed Through", "Square D", "HOM816M200PFTRB", "each", "0.00", "4.00"),
    ("Square D Homeline Generator Interlock Kit 150-225A Indoor", "Square D", "HOMCGK2C", "each", "0.00", "0.75"),
    ("Square D Homeline Generator Interlock Kit 100-125A Indoor", "Square D", "HOMCGK1C", "each", "0.00", "0.75"),
    ("Square D Homeline Indoor Flush Cover", "Square D", "Homeline Cover", "each", "0.00", "0.25"),
    ("Square D Homeline Indoor Surface Cover", "Square D", "Homeline Cover", "each", "0.00", "0.25"),
    ("Square D Homeline Outdoor Cover", "Square D", "Homeline Outdoor Cover", "each", "0.00", "0.25"),
    ("Square D Homeline Ground Bar Kit", "Square D", "PK15GTACP", "each", "0.00", "0.15"),
    ("Square D Homeline Neutral Lug Kit", "Square D", "LK100AN", "each", "0.00", "0.15"),
    ("Square D Homeline Filler Plates", "Square D", "HOMFP", "each", "0.00", "0.02"),
    ("Square D Homeline Whole Home Surge Protector", "Square D", "HOM2175SB", "each", "0.00", "0.50"),

    # =====================================================
    # SQUARE D HOMELINE STANDARD BREAKERS
    # =====================================================
    ("Square D Homeline 15A Single Pole Breaker", "Square D", "HOM115", "each", "0.00", "0.15"),
    ("Square D Homeline 20A Single Pole Breaker", "Square D", "HOM120", "each", "0.00", "0.15"),
    ("Square D Homeline 25A Single Pole Breaker", "Square D", "HOM125", "each", "0.00", "0.15"),
    ("Square D Homeline 30A Single Pole Breaker", "Square D", "HOM130", "each", "0.00", "0.15"),

    ("Square D Homeline 15A Two Pole Breaker", "Square D", "HOM215", "each", "0.00", "0.20"),
    ("Square D Homeline 20A Two Pole Breaker", "Square D", "HOM220", "each", "0.00", "0.20"),
    ("Square D Homeline 25A Two Pole Breaker", "Square D", "HOM225", "each", "0.00", "0.20"),
    ("Square D Homeline 30A Two Pole Breaker", "Square D", "HOM230", "each", "0.00", "0.20"),
    ("Square D Homeline 35A Two Pole Breaker", "Square D", "HOM235", "each", "0.00", "0.20"),
    ("Square D Homeline 40A Two Pole Breaker", "Square D", "HOM240", "each", "0.00", "0.20"),
    ("Square D Homeline 45A Two Pole Breaker", "Square D", "HOM245", "each", "0.00", "0.20"),
    ("Square D Homeline 50A Two Pole Breaker", "Square D", "HOM250", "each", "0.00", "0.20"),
    ("Square D Homeline 60A Two Pole Breaker", "Square D", "HOM260", "each", "0.00", "0.20"),
    ("Square D Homeline 70A Two Pole Breaker", "Square D", "HOM270", "each", "0.00", "0.25"),
    ("Square D Homeline 80A Two Pole Breaker", "Square D", "HOM280", "each", "0.00", "0.25"),
    ("Square D Homeline 90A Two Pole Breaker", "Square D", "HOM290", "each", "0.00", "0.25"),
    ("Square D Homeline 100A Two Pole Breaker", "Square D", "HOM2100", "each", "0.00", "0.25"),
    ("Square D Homeline 125A Two Pole Breaker", "Square D", "HOM2125", "each", "0.00", "0.30"),

    # =====================================================
    # SQUARE D HOMELINE AFCI / GFCI / DUAL FUNCTION
    # =====================================================
    ("Square D Homeline 15A CAFI Breaker", "Square D", "HOM115CAFIC", "each", "0.00", "0.20"),
    ("Square D Homeline 20A CAFI Breaker", "Square D", "HOM120CAFIC", "each", "0.00", "0.20"),
    ("Square D Homeline 15A GFCI Breaker", "Square D", "HOM115GFI", "each", "0.00", "0.20"),
    ("Square D Homeline 20A GFCI Breaker", "Square D", "HOM120GFI", "each", "0.00", "0.20"),
    ("Square D Homeline 30A 2P GFCI Breaker", "Square D", "HOM230GFI", "each", "0.00", "0.25"),
    ("Square D Homeline 40A 2P GFCI Breaker", "Square D", "HOM240GFI", "each", "0.00", "0.25"),
    ("Square D Homeline 50A 2P GFCI Breaker", "Square D", "HOM250GFI", "each", "0.00", "0.25"),
    ("Square D Homeline 60A 2P GFCI Breaker", "Square D", "HOM260GFI", "each", "0.00", "0.25"),
    ("Square D Homeline 15A Dual Function Breaker", "Square D", "HOM115PDFC", "each", "0.00", "0.20"),
    ("Square D Homeline 20A Dual Function Breaker", "Square D", "HOM120PDFC", "each", "0.00", "0.20"),

    # =====================================================
    # SQUARE D HOMELINE TANDEM / QUAD BREAKERS
    # =====================================================
    ("Square D Homeline Tandem 15/15A Breaker", "Square D", "HOMT1515", "each", "0.00", "0.20"),
    ("Square D Homeline Tandem 15/20A Breaker", "Square D", "HOMT1520", "each", "0.00", "0.20"),
    ("Square D Homeline Tandem 20/20A Breaker", "Square D", "HOMT2020", "each", "0.00", "0.20"),
    ("Square D Homeline Quad 20/30A Breaker", "Square D", "HOMT2020230", "each", "0.00", "0.30"),
    ("Square D Homeline Quad 20/50A Breaker", "Square D", "HOMT2020250", "each", "0.00", "0.30"),
    ("Square D Homeline Quad 30/50A Breaker", "Square D", "HOMT3030250", "each", "0.00", "0.30"),

    # =====================================================
    # SERVICE / PANEL MATERIALS
    # =====================================================
    ("200A Meter Main Combination", "Square D", "Homeline Meter Main", "each", "0.00", "5.00"),
    ("200A Meter Socket Ringless", "Milbank", "200A Ringless", "each", "0.00", "2.00"),
    ("200A Meter Socket Ring Type", "Milbank", "200A Ring Type", "each", "0.00", "2.00"),
    ("200A Service Mast Kit", "Generic", "Service Mast Kit", "each", "0.00", "3.00"),
    ("2 Inch Rigid Service Mast", "Allied", "2 RMC", "ft", "0.00", "0.12"),
    ("2 Inch Weatherhead", "Sigma", "2 Weatherhead", "each", "0.00", "0.35"),
    ("2 Inch Rigid Locknut", "Sigma", "2 Locknut", "each", "0.00", "0.03"),
    ("2 Inch Rigid Bushing", "Sigma", "2 Bushing", "each", "0.00", "0.03"),
    ("2 Inch Service Entrance Strap", "Sigma", "2 Strap", "each", "0.00", "0.03"),
    ("Service Entrance Cable 4/0 Aluminum SER", "Southwire", "4/0-4/0-4/0-2/0 SER", "ft", "0.00", "0.08"),
    ("Service Entrance Cable 2/0 Aluminum SER", "Southwire", "2/0 SER", "ft", "0.00", "0.07"),
    ("Service Entrance Cable #2 Aluminum SER", "Southwire", "#2 SER", "ft", "0.00", "0.06"),
    ("Service Entrance Cable #4 Aluminum SER", "Southwire", "#4 SER", "ft", "0.00", "0.05"),
    ("4/0 Aluminum XHHW Conductor", "Southwire", "4/0 AL XHHW", "ft", "0.00", "0.04"),
    ("2/0 Aluminum XHHW Conductor", "Southwire", "2/0 AL XHHW", "ft", "0.00", "0.035"),
    ("#2 Aluminum XHHW Conductor", "Southwire", "#2 AL XHHW", "ft", "0.00", "0.03"),
    ("#4 Aluminum XHHW Conductor", "Southwire", "#4 AL XHHW", "ft", "0.00", "0.025"),

    # =====================================================
    # GROUNDING / BONDING
    # =====================================================
    ("8 ft Ground Rod", "Erico", "5/8 Ground Rod", "each", "0.00", "0.40"),
    ("Ground Rod Clamp", "Erico", "Acorn Clamp", "each", "0.00", "0.10"),
    ("#6 Bare Copper Ground Wire", "Southwire", "#6 Bare Copper", "ft", "0.00", "0.03"),
    ("#4 Bare Copper Ground Wire", "Southwire", "#4 Bare Copper", "ft", "0.00", "0.04"),
    ("#2 Bare Copper Ground Wire", "Southwire", "#2 Bare Copper", "ft", "0.00", "0.05"),
    ("Intersystem Bonding Bridge", "Arlington", "IBTB", "each", "0.00", "0.25"),
    ("Bonding Bushing 1 Inch", "Bridgeport", "1 Bonding Bushing", "each", "0.00", "0.10"),
    ("Bonding Bushing 1-1/4 Inch", "Bridgeport", "1-1/4 Bonding Bushing", "each", "0.00", "0.10"),
    ("Bonding Bushing 1-1/2 Inch", "Bridgeport", "1-1/2 Bonding Bushing", "each", "0.00", "0.12"),
    ("Bonding Bushing 2 Inch", "Bridgeport", "2 Bonding Bushing", "each", "0.00", "0.12"),
    ("Water Pipe Ground Clamp", "Erico", "Pipe Ground Clamp", "each", "0.00", "0.10"),

    # =====================================================
    # NM-B CABLE / BRANCH CIRCUITS
    # =====================================================
    ("14/2 NM-B Cable", "Southwire", "14/2 NM-B", "ft", "0.00", "0.02"),
    ("14/3 NM-B Cable", "Southwire", "14/3 NM-B", "ft", "0.00", "0.025"),
    ("12/2 NM-B Cable", "Southwire", "12/2 NM-B", "ft", "0.00", "0.025"),
    ("12/3 NM-B Cable", "Southwire", "12/3 NM-B", "ft", "0.00", "0.03"),
    ("10/2 NM-B Cable", "Southwire", "10/2 NM-B", "ft", "0.00", "0.04"),
    ("10/3 NM-B Cable", "Southwire", "10/3 NM-B", "ft", "0.00", "0.045"),
    ("8/3 NM-B Cable", "Southwire", "8/3 NM-B", "ft", "0.00", "0.06"),
    ("6/3 NM-B Cable", "Southwire", "6/3 NM-B", "ft", "0.00", "0.08"),
    ("4/3 SER Feeder Cable", "Southwire", "4/3 SER", "ft", "0.00", "0.08"),
    ("2/3 SER Feeder Cable", "Southwire", "2/3 SER", "ft", "0.00", "0.09"),

    # =====================================================
    # THHN / THWN CONDUCTORS
    # =====================================================
    ("#14 THHN Copper Black", "Southwire", "#14 THHN Black", "ft", "0.00", "0.015"),
    ("#14 THHN Copper White", "Southwire", "#14 THHN White", "ft", "0.00", "0.015"),
    ("#14 THHN Copper Green", "Southwire", "#14 THHN Green", "ft", "0.00", "0.015"),
    ("#12 THHN Copper Black", "Southwire", "#12 THHN Black", "ft", "0.00", "0.018"),
    ("#12 THHN Copper White", "Southwire", "#12 THHN White", "ft", "0.00", "0.018"),
    ("#12 THHN Copper Green", "Southwire", "#12 THHN Green", "ft", "0.00", "0.018"),
    ("#10 THHN Copper Black", "Southwire", "#10 THHN Black", "ft", "0.00", "0.025"),
    ("#10 THHN Copper White", "Southwire", "#10 THHN White", "ft", "0.00", "0.025"),
    ("#10 THHN Copper Green", "Southwire", "#10 THHN Green", "ft", "0.00", "0.025"),
    ("#8 THHN Copper Black", "Southwire", "#8 THHN Black", "ft", "0.00", "0.035"),
    ("#8 THHN Copper White", "Southwire", "#8 THHN White", "ft", "0.00", "0.035"),
    ("#8 THHN Copper Green", "Southwire", "#8 THHN Green", "ft", "0.00", "0.035"),
    ("#6 THHN Copper Black", "Southwire", "#6 THHN Black", "ft", "0.00", "0.045"),
    ("#6 THHN Copper White", "Southwire", "#6 THHN White", "ft", "0.00", "0.045"),
    ("#6 THHN Copper Green", "Southwire", "#6 THHN Green", "ft", "0.00", "0.045"),

    # =====================================================
    # BOXES / RINGS
    # =====================================================
    ("1-Gang Plastic Nail-On Box", "Carlon", "1G Nail-On", "each", "0.00", "0.10"),
    ("2-Gang Plastic Nail-On Box", "Carlon", "2G Nail-On", "each", "0.00", "0.12"),
    ("3-Gang Plastic Nail-On Box", "Carlon", "3G Nail-On", "each", "0.00", "0.15"),
    ("4-Gang Plastic Nail-On Box", "Carlon", "4G Nail-On", "each", "0.00", "0.18"),
    ("Old Work 1-Gang Box", "Carlon", "1G Old Work", "each", "0.00", "0.20"),
    ("Old Work 2-Gang Box", "Carlon", "2G Old Work", "each", "0.00", "0.25"),
    ("Old Work 3-Gang Box", "Carlon", "3G Old Work", "each", "0.00", "0.30"),
    ("4 Inch Round Ceiling Box", "Carlon", "Round Box", "each", "0.00", "0.15"),
    ("Ceiling Fan Rated Box", "Raco", "Fan Rated Box", "each", "0.00", "0.40"),
    ("Adjustable Fan Brace Box", "Raco", "Fan Brace", "each", "0.00", "0.60"),
    ("4 Inch Square Metal Box", "Raco", "4S Box", "each", "0.00", "0.15"),
    ("4-11/16 Inch Square Metal Box", "Raco", "411 Box", "each", "0.00", "0.18"),
    ("Single Gang Mud Ring", "Raco", "1G Mud Ring", "each", "0.00", "0.08"),
    ("Two Gang Mud Ring", "Raco", "2G Mud Ring", "each", "0.00", "0.10"),
    ("4 Inch Round Blank Cover", "Raco", "Round Blank", "each", "0.00", "0.05"),
    ("4 Inch Square Blank Cover", "Raco", "4S Blank", "each", "0.00", "0.05"),

    # =====================================================
    # DEVICES / TRIM
    # =====================================================
    ("15A Duplex Receptacle", "Leviton", "15A Duplex", "each", "0.00", "0.15"),
    ("20A Duplex Receptacle", "Leviton", "20A Duplex", "each", "0.00", "0.15"),
    ("15A Tamper Resistant Receptacle", "Leviton", "15A TR", "each", "0.00", "0.15"),
    ("20A Tamper Resistant Receptacle", "Leviton", "20A TR", "each", "0.00", "0.15"),
    ("15A Decora Receptacle", "Leviton", "15A Decora", "each", "0.00", "0.15"),
    ("20A Decora Receptacle", "Leviton", "20A Decora", "each", "0.00", "0.15"),
    ("USB Receptacle", "Leviton", "USB Receptacle", "each", "0.00", "0.25"),
    ("GFCI Receptacle", "Leviton", "GFCI", "each", "0.00", "0.25"),
    ("Weather Resistant GFCI Receptacle", "Leviton", "WR GFCI", "each", "0.00", "0.25"),
    ("AFCI/GFCI Receptacle", "Leviton", "Dual Function Receptacle", "each", "0.00", "0.30"),
    ("Single Pole Switch", "Leviton", "Single Pole", "each", "0.00", "0.15"),
    ("3-Way Switch", "Leviton", "3-Way", "each", "0.00", "0.20"),
    ("4-Way Switch", "Leviton", "4-Way", "each", "0.00", "0.25"),
    ("Decora Single Pole Switch", "Leviton", "Decora SP", "each", "0.00", "0.15"),
    ("Decora 3-Way Switch", "Leviton", "Decora 3W", "each", "0.00", "0.20"),
    ("Dimmer Switch", "Lutron", "Dimmer", "each", "0.00", "0.30"),
    ("Smart Switch", "Lutron", "Smart Switch", "each", "0.00", "0.45"),
    ("Timer Switch", "Intermatic", "Timer Switch", "each", "0.00", "0.35"),
    ("Occupancy Sensor Switch", "Leviton", "Occ Sensor", "each", "0.00", "0.35"),

    # =====================================================
    # WALL PLATES
    # =====================================================
    ("1-Gang Decora Plate", "Leviton", "1G Decora", "each", "0.00", "0.03"),
    ("2-Gang Decora Plate", "Leviton", "2G Decora", "each", "0.00", "0.04"),
    ("3-Gang Decora Plate", "Leviton", "3G Decora", "each", "0.00", "0.05"),
    ("4-Gang Decora Plate", "Leviton", "4G Decora", "each", "0.00", "0.06"),
    ("1-Gang Toggle Plate", "Leviton", "1G Toggle", "each", "0.00", "0.03"),
    ("2-Gang Toggle Plate", "Leviton", "2G Toggle", "each", "0.00", "0.04"),
    ("Blank Cover Plate", "Leviton", "Blank", "each", "0.00", "0.03"),
    ("Duplex Receptacle Plate", "Leviton", "Duplex Plate", "each", "0.00", "0.03"),
    ("Oversized Decora Plate", "Leviton", "Jumbo Decora", "each", "0.00", "0.03"),
    ("Weatherproof In-Use Cover", "TayMac", "In-Use Cover", "each", "0.00", "0.20"),
    ("Weatherproof While-In-Use Extra Duty Cover", "TayMac", "Extra Duty Cover", "each", "0.00", "0.25"),

    # =====================================================
    # CONDUIT / RACEWAY
    # =====================================================
    ("1/2 EMT Conduit", "Allied", "1/2 EMT", "ft", "0.00", "0.04"),
    ("3/4 EMT Conduit", "Allied", "3/4 EMT", "ft", "0.00", "0.05"),
    ("1 Inch EMT Conduit", "Allied", "1 EMT", "ft", "0.00", "0.06"),
    ("1-1/4 Inch EMT Conduit", "Allied", "1-1/4 EMT", "ft", "0.00", "0.08"),
    ("1/2 PVC Conduit Schedule 40", "Cantex", "1/2 PVC SCH40", "ft", "0.00", "0.04"),
    ("3/4 PVC Conduit Schedule 40", "Cantex", "3/4 PVC SCH40", "ft", "0.00", "0.05"),
    ("1 Inch PVC Conduit Schedule 40", "Cantex", "1 PVC SCH40", "ft", "0.00", "0.06"),
    ("1-1/4 Inch PVC Conduit Schedule 40", "Cantex", "1-1/4 PVC SCH40", "ft", "0.00", "0.08"),
    ("1-1/2 Inch PVC Conduit Schedule 40", "Cantex", "1-1/2 PVC SCH40", "ft", "0.00", "0.10"),
    ("2 Inch PVC Conduit Schedule 40", "Cantex", "2 PVC SCH40", "ft", "0.00", "0.12"),
    ("1/2 Liquidtight Flexible Conduit", "Southwire", "1/2 LFMC", "ft", "0.00", "0.07"),
    ("3/4 Liquidtight Flexible Conduit", "Southwire", "3/4 LFMC", "ft", "0.00", "0.08"),
    ("1 Inch Liquidtight Flexible Conduit", "Southwire", "1 LFMC", "ft", "0.00", "0.10"),
    ("Wiremold Surface Raceway", "Legrand", "Wiremold 500", "ft", "0.00", "0.08"),

    # =====================================================
    # FITTINGS
    # =====================================================
    ("1/2 EMT Connector", "Halex", "1/2 EMT Connector", "each", "0.00", "0.03"),
    ("3/4 EMT Connector", "Halex", "3/4 EMT Connector", "each", "0.00", "0.03"),
    ("1 Inch EMT Connector", "Halex", "1 EMT Connector", "each", "0.00", "0.04"),
    ("1/2 EMT Coupling", "Halex", "1/2 EMT Coupling", "each", "0.00", "0.02"),
    ("3/4 EMT Coupling", "Halex", "3/4 EMT Coupling", "each", "0.00", "0.02"),
    ("1 Inch EMT Coupling", "Halex", "1 EMT Coupling", "each", "0.00", "0.03"),
    ("1/2 PVC Male Adapter", "Cantex", "1/2 PVC MA", "each", "0.00", "0.02"),
    ("3/4 PVC Male Adapter", "Cantex", "3/4 PVC MA", "each", "0.00", "0.02"),
    ("1 Inch PVC Male Adapter", "Cantex", "1 PVC MA", "each", "0.00", "0.03"),
    ("1/2 PVC Coupling", "Cantex", "1/2 PVC Coupling", "each", "0.00", "0.02"),
    ("3/4 PVC Coupling", "Cantex", "3/4 PVC Coupling", "each", "0.00", "0.02"),
    ("1 Inch PVC Coupling", "Cantex", "1 PVC Coupling", "each", "0.00", "0.03"),
    ("1/2 PVC LB", "Cantex", "1/2 PVC LB", "each", "0.00", "0.08"),
    ("3/4 PVC LB", "Cantex", "3/4 PVC LB", "each", "0.00", "0.08"),
    ("1 Inch PVC LB", "Cantex", "1 PVC LB", "each", "0.00", "0.10"),
    ("1/2 Liquidtight Connector Straight", "Halex", "1/2 LT Straight", "each", "0.00", "0.05"),
    ("3/4 Liquidtight Connector Straight", "Halex", "3/4 LT Straight", "each", "0.00", "0.05"),
    ("1/2 Liquidtight Connector 90 Degree", "Halex", "1/2 LT 90", "each", "0.00", "0.06"),
    ("3/4 Liquidtight Connector 90 Degree", "Halex", "3/4 LT 90", "each", "0.00", "0.06"),

    # =====================================================
    # LIGHTING / FANS
    # =====================================================
    ("6 Inch LED Recessed Wafer Light", "Halo", "6 LED Wafer", "each", "0.00", "0.30"),
    ("4 Inch LED Recessed Wafer Light", "Halo", "4 LED Wafer", "each", "0.00", "0.25"),
    ("6 Inch Recessed Can Housing", "Halo", "6 Can", "each", "0.00", "0.40"),
    ("6 Inch LED Trim Kit", "Halo", "6 LED Trim", "each", "0.00", "0.15"),
    ("Ceiling Fan", "Customer Supplied", "Fan", "each", "0.00", "1.25"),
    ("Ceiling Light Fixture", "Customer Supplied", "Light Fixture", "each", "0.00", "0.75"),
    ("Bathroom Exhaust Fan", "Broan", "Bath Fan", "each", "0.00", "1.25"),
    ("Vanity Light", "Customer Supplied", "Vanity Light", "each", "0.00", "0.75"),
    ("Chandelier", "Customer Supplied", "Chandelier", "each", "0.00", "1.50"),
    ("Flood Light", "Lithonia", "Flood Light", "each", "0.00", "0.75"),
    ("Landscape Transformer", "Hampton Bay", "LV Transformer", "each", "0.00", "0.75"),

    # =====================================================
    # APPLIANCE / SPECIALTY CIRCUITS
    # =====================================================
    ("Range Receptacle 50A", "Leviton", "14-50R", "each", "0.00", "0.25"),
    ("Dryer Receptacle 30A", "Leviton", "14-30R", "each", "0.00", "0.25"),
    ("AC Disconnect 60A Non-Fused", "Square D", "QO200TR", "each", "0.00", "0.50"),
    ("AC Disconnect 60A Fused", "Square D", "QO200FTR", "each", "0.00", "0.60"),
    ("Whip 1/2 Inch 6 ft", "Southwire", "AC Whip 1/2", "each", "0.00", "0.25"),
    ("Whip 3/4 Inch 6 ft", "Southwire", "AC Whip 3/4", "each", "0.00", "0.25"),
    ("Garbage Disposal Switch Kit", "Leviton", "Disposal Switch", "each", "0.00", "0.50"),
    ("Dishwasher Cord Kit", "Southwire", "DW Cord", "each", "0.00", "0.25"),
    ("Microwave Dedicated Circuit Material", "Generic", "Microwave Circuit", "each", "0.00", "1.00"),
    ("Water Heater Disconnect", "Square D", "Water Heater Disconnect", "each", "0.00", "0.50"),

    # =====================================================
    # EV / GENERATOR / BACKUP POWER
    # =====================================================
    ("NEMA 14-50 EV Receptacle", "Leviton", "14-50R EV", "each", "0.00", "0.35"),
    ("50A EV Circuit Material Allowance", "Generic", "EV 50A Circuit", "each", "0.00", "2.50"),
    ("60A EV Hardwire Circuit Material Allowance", "Generic", "EV 60A Circuit", "each", "0.00", "2.75"),
    ("Generator Inlet 30A", "Reliance", "30A Inlet", "each", "0.00", "0.60"),
    ("Generator Inlet 50A", "Reliance", "50A Inlet", "each", "0.00", "0.75"),
    ("Generator Power Cord 30A", "Reliance", "30A Generator Cord", "each", "0.00", "0.10"),
    ("Generator Power Cord 50A", "Reliance", "50A Generator Cord", "each", "0.00", "0.10"),

    # =====================================================
    # LOW VOLTAGE / DATA / DOORBELL / SMOKE
    # =====================================================
    ("Doorbell Transformer", "Nutone", "16V Transformer", "each", "0.00", "0.35"),
    ("Doorbell Chime", "Nutone", "Chime", "each", "0.00", "0.35"),
    ("Cat6 Cable", "Southwire", "Cat6", "ft", "0.00", "0.02"),
    ("Coax Cable RG6", "Southwire", "RG6", "ft", "0.00", "0.02"),
    ("Data Wall Plate", "Leviton", "Data Plate", "each", "0.00", "0.10"),
    ("Keystone Jack Cat6", "Leviton", "Cat6 Keystone", "each", "0.00", "0.08"),
    ("Smoke Detector Hardwired", "Kidde", "Smoke Hardwired", "each", "0.00", "0.35"),
    ("Smoke/CO Detector Hardwired", "Kidde", "Smoke CO Hardwired", "each", "0.00", "0.40"),
    ("Smoke Detector Remodel Box", "Carlon", "Smoke Box", "each", "0.00", "0.15"),

    # =====================================================
    # CONSUMABLES / FASTENERS
    # =====================================================
    ("NM Cable Staples", "Gardner Bender", "NM Staples", "box", "0.00", "0.05"),
    ("Red Wire Nuts", "Ideal", "Red Wire Nut", "each", "0.00", "0.01"),
    ("Yellow Wire Nuts", "Ideal", "Yellow Wire Nut", "each", "0.00", "0.01"),
    ("Blue Wire Nuts", "Ideal", "Blue Wire Nut", "each", "0.00", "0.01"),
    ("Wago 2-Port Lever Connector", "Wago", "221-412", "each", "0.00", "0.01"),
    ("Wago 3-Port Lever Connector", "Wago", "221-413", "each", "0.00", "0.01"),
    ("Ground Screws", "Ideal", "Ground Screw", "each", "0.00", "0.01"),
    ("Electrical Tape", "3M", "Super 33+", "roll", "0.00", "0.02"),
    ("Anti-Ox Compound", "Noalox", "Anti-Ox", "tube", "0.00", "0.02"),
    ("Zip Ties", "Generic", "Cable Ties", "bag", "0.00", "0.02"),
    ("Self-Tapping Screws", "Generic", "Tek Screws", "box", "0.00", "0.03"),
    ("Masonry Anchors", "Tapcon", "Tapcon", "box", "0.00", "0.05"),
    ("Duct Seal", "Gardner Bender", "Duct Seal", "brick", "0.00", "0.03"),
    ("Fire Caulk", "3M", "Fire Caulk", "tube", "0.00", "0.05"),
]

        created = 0
        updated = 0

        for name, manufacturer, part_number, unit, unit_cost, labor_hours in materials:

            obj, was_created = MaterialCatalog.objects.update_or_create(
                name=name,
                defaults={
                    "manufacturer": manufacturer,
                    "part_number": part_number,
                    "unit": unit,
                    "unit_cost": Decimal(unit_cost),
                    "labor_hours": Decimal(labor_hours),
                    "active": True,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created} materials. Updated {updated} materials."
            )
        )