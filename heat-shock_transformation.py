from opentrons import protocol_api

metadata= {
    'protocolName':'heat-shock_transformation',
    'author':'Carolin Müller, Vera Waffenschnmidt',
    'description' : 'Protocol for E. coli heat-shock transformation using the Opentrons OT-2 with Thermocycler Module. Important note: All agar plates must have a uniform filling level. When teaching, the pipette tip must reach into the agar so that the cell suspension is dispensed onto the agar plate.',
    'apiLevel':'2.1'}

def run(protocol: protocol_api.ProtocolContext):

    # load module
    tc_mod = protocol.load_module ('Thermocycler Module')

    # load labware, adjust if necessary
    tc_plate = tc_mod.load_labware ('biorad_96_wellplate_200ul_pcr')                              
    tiprack_300 = protocol.load_labware ('vwr_96_tiprack_300ul', '3')
    tiprack_20 = protocol.load_labware ('vwr_96_tiprack_10ul_short', '6')   
    reservoir = protocol.load_labware ('agilent_12_reservoir_21ml', '9')    # fill first column with SOC medium
    agarplate_1 = protocol.load_labware ('agarplate_96_wellplate_5ul', '1') # for every 3 columns of samples in the "tc_plate" one agar plate is needed
    agarplate_2 = protocol.load_labware ('agarplate_96_wellplate_5ul', '2')
    agarplate_3 = protocol.load_labware ('agarplate_96_wellplate_5ul', '5')
    agarplate_4 = protocol.load_labware ('agarplate_96_wellplate_5ul', '4')

    # load pipettes
    p300multi = protocol.load_instrument ('p300_multi_gen2', 'left', tip_racks=[tiprack_300])
    p20multi = protocol.load_instrument ('p20_multi_gen2', 'right', tip_racks = [tiprack_20])

    # define columns with used wells (only complete columns possible)
    well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6','A7', 'A8', 'A9', 'A10', 'A11', 'A12'] 

    # cool down thermocycler
    tc_mod.set_block_temperature (0)

    # insert plate and perform the heat-shock
    tc_mod.open_lid ()
    protocol.pause ('Please load PCR plate containing 2 µl DNA and 20 µl competent E. coli cells per well into the thermocycler block')
    tc_mod.close_lid ()

    # heat-shock transformation
    tc_mod.set_block_temperature (0, hold_time_minutes=30, block_max_volume=22)
    tc_mod.set_block_temperature (42, hold_time_seconds=30, block_max_volume=22)
    tc_mod.set_block_temperature (0, hold_time_minutes=2, block_max_volume=22)


    # transfer SOC medium into PCR plate for regeneration
    tc_mod.open_lid ()
    p300multi.transfer(178,reservoir.wells_by_name()['A1'],[tc_plate.wells_by_name ()[well_name] for well_name in well_list], mix_after = (2, 190), new_tip = 'always')
    tc_mod.close_lid ()
    tc_mod.set_lid_temperature(40)
    tc_mod.set_block_temperature (37, hold_time_minutes=60, block_max_volume=200)

    # pipette cell suspension onto the agar plates
    tc_mod.open_lid ()
    tc_mod.deactivate_lid()
    spot_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6','A7', 'A8', 'A9', 'A10', 'A11', 'A12'] # do not change!
    i = 0
    while i < len(well_list):
        p20multi.pick_up_tip()  
        if i <= 2:
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_1 [spot_list [i * 4]])
            p20multi.dispense (8, agarplate_1 [spot_list [i * 4 + 1]])
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_1 [spot_list [i * 4 + 2]])
            p20multi.dispense (8, agarplate_1 [spot_list [i * 4 + 3]])
        if i > 2 and i <= 5:
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_2 [spot_list [(i - 3) * 4]])
            p20multi.dispense (8, agarplate_2 [spot_list [(i - 3) * 4 + 1]])
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_2 [spot_list [(i - 3) * 4 + 2]])
            p20multi.dispense (8, agarplate_2 [spot_list [(i - 3) * 4 + 3]])
        if i > 5 and i <= 8:
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_3 [spot_list [(i - 6) * 4 ]])
            p20multi.dispense (8, agarplate_3 [spot_list [(i - 6) * 4 + 1]])
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_3 [spot_list [(i - 6) * 4 + 2]])
            p20multi.dispense (8, agarplate_3 [spot_list [(i - 6) * 4 + 3]])
        if i > 8 and i <= 11:
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_4 [spot_list [(i - 9) * 4]])
            p20multi.dispense (8, agarplate_4 [spot_list [(i - 9) * 4 + 1]])
            p20multi.aspirate (17, tc_plate [well_list [i]]) 
            p20multi.dispense (8, agarplate_4 [spot_list [(i - 9) * 4 + 2]])
            p20multi.dispense (8, agarplate_4 [spot_list [(i - 9) * 4 + 3]])
        p20multi.drop_tip()
        i= i + 1