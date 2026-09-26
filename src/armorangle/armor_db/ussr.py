# GENERATED FILE - DO NOT EDIT BY HAND
#
# Regenerate with generate_armor_db.py (build_wotmod.py already does this
# automatically as its first step). Source of truth: armor_data/vehicles.json

from armorangle.armor_db import ArmorPlate, VehicleArmor, mirroredPair


ARMOR_DB = {
    # mm/slope/bearing values hand-filled by the user directly - still TODO verify against Tankopedia / live test.
    'ussr:R01_IS': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='front-upper', bearingDeg=0, slopeDeg=27, nominalMm=120)] +
            [ArmorPlate(label='front-lower', bearingDeg=0, slopeDeg=-29, nominalMm=100)] +
            mirroredPair(label='shoulder', bearingDeg=50, slopeDeg=13, nominalMm=100)
        ),
        sidePlates=(
            mirroredPair(label='side upper', bearingDeg=90, slopeDeg=13, nominalMm=90) +
            mirroredPair(label='side lower', bearingDeg=90, slopeDeg=0, nominalMm=90)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # armor data not filled in yet, HUD shows nothing for this vehicle until frontPlates/sidePlates are filled in and generate_armor_db.py is re-run.
    'ussr:R19_IS-3': VehicleArmor(
        frontPlates=[],
        sidePlates=[],
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # mm/slope values hand-filled by the user directly - still TODO verify against Tankopedia / live test.
    # Side armor is a single flat plate (no upper/lower split), so only one sidePlates entry (routes to the side_upper UI slot; side_lower stays hidden for this vehicle).
    'ussr:R72_T150': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='upper glacis', bearingDeg=0, slopeDeg=29, nominalMm=90)] +
            [ArmorPlate(label='lower glacis', bearingDeg=0, slopeDeg=-29, nominalMm=90)]
        ),
        sidePlates=(
            mirroredPair(label='side', bearingDeg=90, slopeDeg=0, nominalMm=90)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # Shape (bearingDeg/slopeDeg) copied from ussr:R72_T150 per the user - same hull layout, just
    # uniformly 75mm on every plate instead of T-150's 90mm. Still TODO verify against Tankopedia / live test.
    'ussr:R80_KV1': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='upper glacis', bearingDeg=0, slopeDeg=29, nominalMm=75)] +
            [ArmorPlate(label='lower glacis', bearingDeg=0, slopeDeg=-29, nominalMm=75)]
        ),
        sidePlates=(
            mirroredPair(label='side', bearingDeg=90, slopeDeg=0, nominalMm=75)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

}
