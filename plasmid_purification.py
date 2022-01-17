from opentrons import protocol_api

metadata= {
    'protocolName': 'plasmid_purification',
    'author': 'Carolin Müller, Vera Waffenschnmidt',
    'description': 'Protocol for plasmid purification using the Opentrons OT-2 with Magnetic Module and the Promega Wizard® MagneSil® Plasmid DNA Purification System.',
    'apiLevel':'2.8'}

def run(protocol: protocol_api.ProtocolContext):

    # load module
    magnetic_module = protocol.load_module ('magnetic module gen2', '1')

    # load labware, adjust if necessary
    magnetic_plate = magnetic_module.load_labware ('greiner_96_wellplate_320ul') 
    deck_plate = protocol.load_labware ('greiner_96_wellplate_320ul', '2') 
    reservoir_plate = protocol.load_labware('agilent_12_reservoir_21ml', '3')
    square_plate = protocol.load_labware ('usascientific_96_wellplate_2.4ml_deep', '5')
    tiprack_6 =  protocol.load_labware('vwr_96_tiprack_300ul', 6)
    tiprack_7 =  protocol.load_labware('vwr_96_tiprack_300ul', 7)
    tiprack_8 =  protocol.load_labware('vwr_96_tiprack_300ul', 8)
    tiprack_9 =  protocol.load_labware('vwr_96_tiprack_300ul', 9)
    tiprack_10 = protocol.load_labware('vwr_96_tiprack_300ul', 10)
    tiprack_11 = protocol.load_labware('vwr_96_tiprack_300ul', 11)
    # position 4 could be used for heating elution buffer, for heating the collection plate to dry the pellets after washing, 
    # for an additional culture plate to allow using plates with fewer, but bigger wells or for an additional tiprack to avoid re-usage of tips   
    
    # load pipette (do not change pipette to gen 2, because it affects the default aspirate and dispense speeds. Backwards compatibility should allow attaching a gen 2 pipette and treating it as gen 1
    p_300 = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack_6, tiprack_7, tiprack_8, tiprack_9, tiprack_10, tiprack_11])

    # define columns containing samples
    column_list = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11','A12']

    #define aspiration and dispense speed. 
    p_300.flow_rate.aspirate = 150
    p_300.flow_rate.dispense = 300

    # define magnet height from base of plate
    mag_height = 5.3

    #cell resuspension solution ("Shaking at amplitude 8 for 5 min")
    p_300.starting_tip = tiprack_6.well('A1') 
    p_300.transfer (90, reservoir_plate.wells_by_name ()['A1'], [square_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (10, 70), new_tip = 'always', blow_out = True, blowout_location='destination well')

    #cell lysis solution ("amplitude 6, 3 min")
    p_300.starting_tip = tiprack_7.well('A1') 
    p_300.transfer (120, reservoir_plate.wells_by_name ()['A2'], [square_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (7, 150), new_tip = 'always', blow_out = True, blowout_location='destination well')
    protocol.comment('Pausing operation for 3 minutes to improve lysis.')
    protocol.delay(minutes=3)

    # neutralization buffer ("amplitude 7, 3 min")
    p_300.starting_tip = tiprack_8.well('A1') 
    p_300.transfer (120, reservoir_plate.wells_by_name ()['A3'], [square_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (10, 250), blow_out = True, blowout_location='destination well', new_tip = 'always')
    protocol.comment('Pausing operation for 2 minutes to allow settling of debris.')
    protocol.delay(minutes=2)

    # MagnesilBlue ("amplitude 8, 1 min"), Mixing before aspiration to distribute beads evenly
    # transferring samples to clearing plate
    # Tips used for adding MagnesilBlue are also used to transfer samples to new plate
    p_300.starting_tip = tiprack_9.well('A1') 
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.transfer (25, reservoir_plate.wells_by_name ()['A4'], square_plate [column_list [i]], mix_before = (10, 300), mix_after = (15, 250), new_tip = "never") 
        p_300.transfer (300, square_plate [column_list [i]], magnetic_plate [column_list [i]], blow_out = True, blowout_location='destination well', new_tip = "never") 
        p_300.drop_tip()
        i= i + 1

    # engage magnets and allow pellet to form for 10 min
    magnetic_module.engage (height_from_base = mag_height)
    protocol.comment ('Pausing operation for 7 minutes to allow pellets to form')
    protocol.delay (minutes = 7)

    # MagnesilRed
    p_300.starting_tip = tiprack_10.well('A1') 
    p_300.transfer (50, reservoir_plate.wells_by_name ()['A5'], [deck_plate.wells_by_name ()[well_name] for well_name in column_list], mix_before = (15, 300), blow_out = True, blowout_location='destination well', new_tip = 'once', trash = False)
    p_300.reset_tipracks()

    # carefully transfer samples without pellet to binding plate and mixing with MagnesilRed (2 x 2 min at amplitude 6)
    p_300.starting_tip = tiprack_10.well('A1')
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.aspirate (240, magnetic_plate [column_list [i]], rate = 0.16) # "rate" is the multiplication factor of the pipette's default aspirate flow rate (0.16 = 25 µl/s)
        p_300.dispense (240, deck_plate [column_list [i]], rate = 1)        # "rate" is the multiplication factor of the pipette's default dispense flow rate (1 = 300 µl/s)
        j = 0
        for j in range (15): # mixing repetitions
            p_300.aspirate (250, deck_plate [column_list [i]], rate = 0.66) # = 100 µl/s
            p_300.dispense (250, deck_plate [column_list [i]], rate = 0.33) # = 100 µl/s
        p_300.blow_out () # blow out at current position
        p_300.drop_tip ()
        i = i + 1

    # pause protocol until binding plate is placed on magnetic module and tip racks are refilled
    protocol.pause ('Please discard the clearing plate on the magnetic module and instead place the binding plate from position 2 on the magnetic module. Place a fresh collection plate on position 2. Please refill all tip racks. Press resume to continue protocol.')
    
    # reset tiprack tracking and start again with first tiprack
    p_300.reset_tipracks()

    # allow pellets to form (magnets still engaged)
    protocol.comment ('Pausing operation for 1 minute to allow pellets to form')
    protocol.delay (minutes = 1)

    # discard supernatant
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.starting_tip = tiprack_6.well('A1') 
        p_300.pick_up_tip() 
        p_300.aspirate(265, magnetic_plate [column_list[i]], rate = 0.16) # "rate" is the multiplication factor of the pipette's default aspirate flow rate (0.16 = 25 µl/s)
        p_300.drop_tip()
        i = i + 1

    # Washing with 80% ethanol ("amplitude 4, 1 min")
    p_300.flow_rate.dispense = 300
    magnetic_module.disengage()
    p_300.starting_tip = tiprack_7.well('A1')
    p_300.flow_rate.aspirate = 150
    p_300.transfer (100, reservoir_plate.wells_by_name ()['A6'], [magnetic_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (7, 75), blow_out = True, blowout_location='destination well', new_tip = 'always', trash = False)
    magnetic_module.engage (height_from_base = mag_height)
    protocol.comment ('Pausing operation for 1 minute to allow pellets to form')
    protocol.delay (minutes = 1)    
    p_300.flow_rate.aspirate = 25
    p_300.reset_tipracks()
    p_300.starting_tip = tiprack_7.well('A1')
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.aspirate(90, magnetic_plate [column_list[i]])
        p_300.drop_tip()
        i = i + 1

    magnetic_module.disengage()
    p_300.starting_tip = tiprack_8.well('A1')
    p_300.flow_rate.aspirate = 150
    p_300.transfer (100, reservoir_plate.wells_by_name ()['A7'], [magnetic_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (7, 75), blow_out = True, blowout_location='destination well', new_tip = 'always', trash = False)
    magnetic_module.engage (height_from_base = mag_height)
    protocol.comment ('Pausing operation for 1 minute to allow pellets to form')
    protocol.delay (minutes = 1)
    p_300.flow_rate.aspirate = 25
    p_300.reset_tipracks()
    p_300.starting_tip = tiprack_8.well('A1')
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.aspirate(90, magnetic_plate [column_list[i]])
        p_300.drop_tip()
        i = i + 1

    magnetic_module.disengage()
    p_300.starting_tip = tiprack_9.well('A1')
    p_300.flow_rate.aspirate = 150
    p_300.transfer (100, reservoir_plate.wells_by_name ()['A8'], [magnetic_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (7, 75), blow_out = True, blowout_location='destination well', new_tip = 'always', trash = False)
    magnetic_module.engage (height_from_base = mag_height)
    protocol.comment ('Pausing operation for 1 minutes to allow pellets to form')
    protocol.delay (minutes = 1)
    p_300.flow_rate.aspirate = 25
    p_300.reset_tipracks()
    p_300.starting_tip = tiprack_9.well('A1')
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.aspirate(110, magnetic_plate [column_list[i]])
        p_300.drop_tip()
        i = i + 1

    # drying for at least 10 min
    magnetic_module.disengage()
    protocol.pause ('Pausing protocol execution until pellet has dried. Please press resume when residual ethanol has evaporated (approx. 45 min with air drying, can be accelerated by placing the plate in a drying oven)')
    
    # elution of DNA ("amplitude 6, 2 min")
    p_300.starting_tip = tiprack_10.well('A1')
    i = 0
    while i < len(column_list): #len = number of columns
        p_300.pick_up_tip()
        p_300.aspirate (100, reservoir_plate.wells_by_name ()['A9'], rate = 1) # = 150 µl/s)
        p_300.dispense (100, magnetic_plate [column_list [i]], rate = 1)    # = 300 µl/s)
        j = 0
        for j in range (15): # mixing repetitions
            p_300.aspirate (100, magnetic_plate [column_list [i]], rate = 1) # = 150 µl/s
            p_300.dispense (100, magnetic_plate [column_list [i]], rate = 0.25) # = 75 µl/s
        p_300.blow_out () # blow out at current position
        p_300.return_tip ()
        i = i + 1
    protocol.comment('Pausing operation for 5 minutes to improve elution.')
    protocol.delay(minutes=5)

    p_300.reset_tipracks()
    p_300.starting_tip = tiprack_10.well('A1')
    i = 0
    while i < len(column_list):
        p_300.pick_up_tip()
        j = 0
        for j in range (15): # mixing repetitions
            p_300.aspirate (100, magnetic_plate [column_list [i]], rate = 1) # = 150 µl/s
            p_300.dispense (100, magnetic_plate [column_list [i]], rate = 0.25) # = 75 µl/s
        p_300.blow_out () # blow out at current position
        p_300.drop_tip ()
        i = i + 1
    magnetic_module.engage (height_from_base = mag_height)

    # pausing to pellet residual particles
    protocol.comment ('Pausing operation for 10 minutes to remove residual particles')
    protocol.delay (minutes = 10) 

    # collecting eluate (80 µl - 90 µl) 
    p_300.starting_tip = tiprack_11.well('A1')
    p_300.flow_rate.aspirate = 25
    p_300.transfer (80, [magnetic_plate.wells_by_name ()[well_name] for well_name in column_list], [deck_plate.wells_by_name ()[well_name] for well_name in column_list], blow_out = True, blowout_location='destination well', new_tip = 'always')

    # additional step in case collected eluate is not yet clear
    protocol.pause ('Please check if brown residue can be seen in collection plate on position 2. If this is not the case, you can now stop the protocol and use the purified plasmids in the collection plate. If you do see residue, place the plate from position 2 on the magnetic module and provide a fresh plate for position 2. Fill up tiprack on position 11 and resume.')
    p_300.reset_tipracks()
    p_300.starting_tip = tiprack_11.well('A1') 
    p_300.flow_rate.aspirate = 25
    p_300.transfer (75, [magnetic_plate.wells_by_name ()[well_name] for well_name in column_list], [deck_plate.wells_by_name ()[well_name] for well_name in column_list], blow_out = True, blowout_location='destination well', new_tip = 'always')
