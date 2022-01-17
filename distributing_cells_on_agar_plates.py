from opentrons import protocol_api

metadata= {
    'protocolName':'distributing_cells_on_agar_plates',
    'author':'Carolin Müller, Vera Waffenschnmidt',
    'description' : 'Protocol for distribution of cell suspension to agar plates using the Opentrons OT-2 with Thermocycler Module, e.g., to have more agar plates after E. coli heat-shock transformation. Important note: All agar plates must have a uniform filling level. When teaching, the pipette tip must reach into the agar so that the cell suspension is dispensed onto the agar plate.',
    'apiLevel':'2.1'}

def run(protocol: protocol_api.ProtocolContext):

    # load module
    tc_mod = protocol.load_module ('Thermocycler Module')

    # load labware, adjust if necessary
    tc_plate = tc_mod.load_labware ('biorad_96_wellplate_200ul_pcr')    # plate containing cell suspension
    tiprack_20 = protocol.load_labware ('vwr_96_tiprack_10ul_short', '6')
    agarplate_1 = protocol.load_labware ('agarplate_96_wellplate_5ul', '1') # for every 3 columns of samples in the "tc_plate" one agar plate is needed
    agarplate_2 = protocol.load_labware ('agarplate_96_wellplate_5ul', '2')
    agarplate_3 = protocol.load_labware ('agarplate_96_wellplate_5ul', '5')
    agarplate_4 = protocol.load_labware ('agarplate_96_wellplate_5ul', '4')

    # load pipette
    p20multi = protocol.load_instrument ('p20_multi_gen2', 'right', tip_racks = [tiprack_20])

    # define columns with used wells (only complete columns possible)
    well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6','A7', 'A8', 'A9', 'A10', 'A11', 'A12'] # change list to include all columns with samples.
    
    # Load plate with cells
    tc_mod.open_lid ()
    tc_mod.set_block_temperature (37) # adjust, if necessary
    protocol.pause ('Please load PCR plate containing samples for plating out into the thermocycler block')

    # pipette cell suspension onto the agar plates  
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