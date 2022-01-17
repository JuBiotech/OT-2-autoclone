from opentrons import protocol_api

metadata = {
    'protocolName': 'golden_gate_assembly_mixing',
    'author': 'Carolin Müller, Vera Waffenschmidt',
    'description': 'Protocol for mixing plasmid DNA and reaction mix before Golden Gate assembly using the Opentrons OT-2 with Thermocycler Module.',
    'apiLevel': '2.8'}

def run(protocol: protocol_api.ProtocolContext):
    
    # load module
    tc_mod = protocol.load_module ('Thermocycler Module')

    # load labware, adjust if necessary
    DNA_plate = protocol.load_labware ('biorad_96_wellplate_200ul_pcr', '4') # plate with appropriately diluted DNA samples
    MM_plate = protocol.load_labware('nest_12_reservoir_15ml','9') # 12 column plate with reaction mix in column 1
    tc_plate = tc_mod.load_labware ('biorad_96_wellplate_200ul_pcr')
    tiprack_1 = protocol.load_labware ('opentrons_96_tiprack_20ul', '6')
    tiprack_2 = protocol.load_labware ('opentrons_96_tiprack_20ul', '3')
    
    # load pipettes
    p20multi = protocol.load_instrument ('p20_multi_gen2', 'right', tip_racks = [tiprack_1, tiprack_2])
    
    # define variables
    column_list = ['1', '2', '3', '4', '5', '6','7', '8', '9', '10', '11', '12']
    well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6','A7', 'A8', 'A9', 'A10', 'A11', 'A12'] 

    # transfer plasmid DNA into pcr plate in Thermocycler Module
    p20multi.transfer (10, [DNA_plate.columns_by_name ()[column_name] for column_name in column_list],[tc_plate.columns_by_name ()[column_name] for column_name in column_list], new_tip = 'always', blow_out = True, blowout_location='destination well' )

    # transfer reaction mix into pcr plate and mixing
    p20multi.transfer (10, [MM_plate.wells_by_name ()['A1']],[tc_plate.wells_by_name ()[well_name] for well_name in well_list], mix_after = (3, 10), new_tip = 'always', blow_out = True, blowout_location='destination well' )
