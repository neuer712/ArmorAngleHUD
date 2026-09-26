# GENERATED FILE - DO NOT EDIT BY HAND
#
# Regenerate with generate_armor_db.py (build_wotmod.py already does this
# automatically as its first step). Source of truth: armor_data/vehicles.json

from armorangle.armor_db import ArmorPlate, VehicleArmor, mirroredPair


ARMOR_DB = {
    # mm/slope values still TODO verify against Tankopedia.
    'germany:G04_PzVI_Tiger_I': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='front', bearingDeg=0, slopeDeg=10, nominalMm=100)]
        ),
        sidePlates=(
            mirroredPair(label='side upper', bearingDeg=90, slopeDeg=0, nominalMm=80) +
            mirroredPair(label='side lower', bearingDeg=90, slopeDeg=0, nominalMm=60)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # armor data not filled in yet, HUD shows nothing for this vehicle until frontPlates/sidePlates are filled in and generate_armor_db.py is re-run.
    'germany:G05_StuG_40_AusfG': VehicleArmor(
        frontPlates=[],
        sidePlates=[],
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # armor data not filled in yet, HUD shows nothing for this vehicle until frontPlates/sidePlates are filled in and generate_armor_db.py is re-run.
    'germany:G136_Tiger_131': VehicleArmor(
        frontPlates=[],
        sidePlates=[],
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # mm/slope values hand-filled by the user directly, then sign-corrected (lower glacis and
    # side lower flipped negative relative to upper) after a live elevation test - confirmed correct.
    'germany:G16_PzVIB_Tiger_II': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='upper glacis', bearingDeg=0, slopeDeg=50, nominalMm=160)] +
            [ArmorPlate(label='lower glacis', bearingDeg=0, slopeDeg=-50, nominalMm=100)]
        ),
        sidePlates=(
            mirroredPair(label='side upper', bearingDeg=90, slopeDeg=25, nominalMm=80) +
            mirroredPair(label='side lower', bearingDeg=90, slopeDeg=0, nominalMm=80)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # mm/slope/bearing values hand-filled by the user directly - still TODO verify against Tankopedia / live test.
    # Side armor is a single flat plate (no upper/lower split), so only one sidePlates entry (routes to the side_upper UI slot; side_lower stays hidden for this vehicle).
    'germany:G177_E65_Zwilling': VehicleArmor(
        frontPlates=(
            [ArmorPlate(label='upper glacis', bearingDeg=0, slopeDeg=53, nominalMm=160)] +
            [ArmorPlate(label='lower glacis', bearingDeg=0, slopeDeg=-60, nominalMm=100)] +
            mirroredPair(label='shoulder', bearingDeg=60, slopeDeg=35, nominalMm=120)
        ),
        sidePlates=(
            mirroredPair(label='side', bearingDeg=90, slopeDeg=24, nominalMm=60)
        ),
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # armor data not filled in yet, HUD shows nothing for this vehicle until frontPlates/sidePlates are filled in and generate_armor_db.py is re-run.
    'germany:G43_Sturer_Emil': VehicleArmor(
        frontPlates=[],
        sidePlates=[],
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

    # armor data not filled in yet, HUD shows nothing for this vehicle until frontPlates/sidePlates are filled in and generate_armor_db.py is re-run.
    'germany:G63_PzI_ausf_C': VehicleArmor(
        frontPlates=[],
        sidePlates=[],
        safetyThreshold1=None,
        safetyThreshold2=None
    ),

}
