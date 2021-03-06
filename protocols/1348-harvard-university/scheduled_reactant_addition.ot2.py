from opentrons import labware, instruments

# generate custom labware
custom_6_well_plate = 'custom-6-well-plate'
if custom_6_well_plate not in labware.list():
    labware.create(
        custom_6_well_plate,
        grid=(3, 2),
        spacing=(40, 38),
        diameter=34.9,
        depth=65)

# labware setup
stock = labware.load(custom_6_well_plate, '1')
reactor = labware.load(custom_6_well_plate, '2')

tipracks_300 = [labware.load('opentrons-tiprack-300ul', slot)
                for slot in ['4', '5']]


# pipette setup
p300 = instruments.P300_Single(
    mount='right',
    tip_racks=tipracks_300)


for index, reactor in enumerate(reactor.wells()[:3]):
    if index < 2:
        time = 2
    else:
        time = 1

    # transfer stock 1 to reactor 1
    p300.transfer(400, stock.wells('A1'), reactor)
    p300.delay(minutes=time)

    # repeat transfer stock 2 to reactor 1
    for cycle in range(5):
        p300.transfer(1000, stock.wells('A2'), reactor)
        p300.delay(minutes=time)

    # transfer stock 3 to reactor 1
    for cycle in range(5):
        p300.transfer(250, stock.wells('A3'), reactor)
        p300.delay(minutes=time)

    # transfer stock 4 to reactor 1
    for cycle in range(5):
        p300.transfer(250, stock.wells('B1'), reactor)
        p300.delay(minutes=time)

    # transfer stock 1 to reactor 1
    p300.transfer(400, stock.wells('A1'), reactor)
