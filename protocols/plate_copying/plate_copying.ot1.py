from opentrons import containers, instruments
from otcustomizers import StringSelection

# Be careful not to calibrate the leftmost containers ('A' slots)
# too far to the left. The touch_tip action may make the head hit
# the leftmost limit switch.
#
# Also, you must calibrate carefully to the center well of each plate,
# or the repeated touch_tip action may eventually knock off the tips.

dest_slots = [
    'A1',
    'A2', 'B2', 'C2', 'D2', 'E2',
    'A3', 'B3', 'C3', 'D3', 'E3']

# B1 is not safe to use because of tip rack in D1.

# Hood has no row 3
max_plates_for_hood = len([s for s in dest_slots if s[1] != '3'])

trash = containers.load('trash-box', 'E1')

# TODO: optimize so that you only use 1 tiprack and can use an extra container,
# when you have 96 well source + dest (384 needs 2x tipracks, 96 needs just 1x)
tip_slots = ['D1', 'C1']

tip_racks = [containers.load('tiprack-200ul', slot) for slot in tip_slots]

# TODO: customizable pipette vol
p50multi = instruments.Pipette(
    axis='a',
    channels=8,
    max_volume=50,
    min_volume=5,
    tip_racks=tip_racks,
    trash_container=trash,
)

container_choices = [
    '96-flat', '96-PCR-tall', '96-deep-well', '384-plate']


def alternating_wells(plate, row_num):
    """
    Returns list of 2 WellSeries for the 2 possible positions of an
    8-channel pipette for a row in a 384 well plate.
    """
    return [
        plate.rows(row_num).wells(start_well, length=8, step=2)
        for start_well in ['A', 'B']
    ]


def run_custom_protocol(
        transfer_volume: float=20,
        robot_model: StringSelection('hood', 'not hood')='not hood',
        source_container: StringSelection(*container_choices)='96-flat',
        destination_container: StringSelection(*container_choices)='96-flat',
        number_of_destination_plates: int=4):

    # Load containers
    all_dest_plates = [
        containers.load(destination_container, slotName)
        for slotName in dest_slots]

    source_plate = containers.load(source_container, 'C2')

    if (robot_model == 'hood' and
            number_of_destination_plates > max_plates_for_hood):
        raise Exception((
            'OT Hood model can only accomodate {} plates for ' +
            'this protocol, you entered {}').format(
                max_plates_for_hood, number_of_destination_plates))

    if ('384-plate' in [source_container, destination_container] and
            source_container != destination_container):
        raise Exception(
            'This protocol currently only allows 96:96 or 384:384 transfers.' +
            ' You entered "{}" and "{}"'.format(
                source_container, destination_container))

    row_count = len(all_dest_plates[0].rows())
    dest_plates = all_dest_plates[:number_of_destination_plates]

    # fill row 1 for all plates, then row 2 for all plates, etc
    for row_index in range(row_count):
        if destination_container == '384-plate':
            # Use "alternating wells" trick for 8-channel in 384 plate
            dest_wells = [
                row
                for plate in dest_plates
                for row in alternating_wells(plate, row_index)]

            source_wells = alternating_wells(source_plate, row_index)

        else:
            dest_wells = [plate.rows(row_index) for plate in dest_plates]

            source_wells = source_plate.rows(row_index)

        p50multi.distribute(
            transfer_volume,
            source_wells,
            dest_wells,
            touch_tip=True,
            disposal_vol=0
        )
