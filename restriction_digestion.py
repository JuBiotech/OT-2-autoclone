from opentrons import protocol_api

metadata = {
    'protocolName': 'restriction_digestion',
    'author': 'Carolin Müller, Vera Waffenschmidt',
    'description': 'Protocol for restriction digestion using the Opentrons OT-2 with Thermocycler Module. In this example, two different reaction mixes are added depending on the sample',
    'apiLevel': '2.8'}

def run(protocol: protocol_api.ProtocolContext):
    
    # load module
    tc_mod = protocol.load_module('Thermocycler Module')

    # load labware, adjust if necessary
    tc_plate = tc_mod.load_labware( 'thermofisher_96_pcrplate_200ul')   
    plasmid_plate = protocol.load_labware ('greiner_96_wellplate_320ul', '4')   # plate with plasmid DNA
    mastermix = protocol.load_labware ('thermo_96_chilledpcr_200ul','5')    # plate with reaction mix on 3D printed cooling carrier containing ice
    dilution_plate = protocol.load_labware ('nonskirted_96_wellplate_300ul', '1')   # plate for dilution of digested plasmid DNA for capillary electrophoresis
    water_plate = protocol.load_labware ('nest_96_wellplate_200ul_flat', '2')   # plate filled with distilled water for dilution of digested plasmids for capillary electrophoresis
    tiprack_1 = protocol.load_labware ('vwr_96_tiprack_10ul_short', '3')
    tiprack_2 = protocol.load_labware ('vwr_96_tiprack_10ul_short', '6')

    #load pipette
    p_20multi = protocol.load_instrument ('p20_multi_gen2', 'right', tip_racks = [tiprack_1, tiprack_2])

    #define columns
    column_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6','A7'] # all columns used
    master_list_1 = ['A1', 'A2', 'A3', 'A7']    # columns where first reaction mix is added
    master_list_2 = ['A5', 'A6']        # columns where second reaction mix is added
    
    # transfer 3 µl DNA from plasmid_plate into tc_plate    
    tc_mod.open_lid ()
    p_20multi.transfer (3, [plasmid_plate.wells_by_name ()[well_name] for well_name in column_list], [tc_plate.wells_by_name ()[well_name] for well_name in column_list], new_tip = 'always', blow_out = True, blowout_location='destination well')

    # cool down thermocycler and add plate with reaction mix(es)
    tc_mod.set_block_temperature (0)
    protocol.pause ('Please place PCR plate containing reaction mixes on cooling carrier')     

    # transfer 7 µl reaction mix from first column in first set of samples
    p_20multi.transfer (7, mastermix.wells_by_name ()['A1'], [tc_plate.wells_by_name ()[column_name] for column_name in master_list_1], mix_after = (3, 10), new_tip = 'always', blow_out = True, blowout_location='destination well')

    # transfer 7 µl reaction mix from second column in second set of samples
    p_20multi.transfer (7, mastermix.wells_by_name ()['A2'], [tc_plate.wells_by_name ()[column_name] for column_name in master_list_2], mix_after = (3, 10), new_tip = 'always', blow_out = True, blowout_location='destination well')

    # start digestion, adjust if necessary
    tc_mod.close_lid ()
    tc_mod.set_lid_temperature(40)
    tc_mod.set_block_temperature (37, hold_time_minutes=60, block_max_volume=10)

    # heat inactivation, adjust if necessary
    tc_mod.set_lid_temperature(85)
    tc_mod.set_block_temperature (80, hold_time_minutes=20, block_max_volume=10)
    tc_mod.set_block_temperature (20)
    tc_mod.deactivate()
    tc_mod.open_lid ()

    # fill up tip racks for dilution of digested DNA for capillary electrophoresis
    protocol.pause ('Please fill up tip racks. Press resume to proceed to sample dilution.')
    p_20multi.reset_tipracks()
    p_20multi.starting_tip = tiprack_1.well('A1')
  
    # dispense water into dilution plate for a 3x dilution of DNA samples for capillary electrophoresis, adjust if necessary
    p_20multi.transfer (6, water_plate.wells_by_name ()['A1'], [dilution_plate.wells_by_name ()[well_name] for well_name in column_list], new_tip = 'once', blow_out = True, blowout_location='destination well')

    # dispense DNA samples into dilution plate for a 3x dilution for capillary electrophoresis, adjust if necessary
    p_20multi.transfer (3, [tc_plate.wells_by_name ()[well_name] for well_name in column_list], [dilution_plate.wells_by_name ()[well_name] for well_name in column_list], mix_after = (3, 10), new_tip = 'always', blow_out = True, blowout_location='destination well')
