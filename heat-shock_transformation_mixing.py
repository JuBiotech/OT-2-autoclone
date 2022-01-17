from opentrons import protocol_api

metadata = {
    'protocolName': 'heat-shock_transformation_mixing',
    'author': 'Carolin Müller, Vera Waffenschnmidt',
    'description': 'Protocol for mixing of competent cells and DNA before E. coli heat-shock transformation using the Opentrons OT-2 with Thermocycler Module.',
    'apiLevel': '2.8'}

def run(protocol: protocol_api.ProtocolContext):
    
    # load module
    tc_mod = protocol.load_module ('Thermocycler Module')

    # load labware, adjust if necessary
    DNA_plate = protocol.load_labware ('thermofisher_96_pcrplate_200ul', '4')   # plate with DNA samples, e.g., after Golden Gate assembly
    tc_plate = tc_mod.load_labware ('thermofisher_96_pcrplate_200ul')   # plate with competent cells, placed into the Thermocycler Module during the experiment
    tiprack_20 = protocol.load_labware ('vwr_96_tiprack_10ul_short', '6')
    
    # labware for heat-shock transformation only (do not occupy these positions)
    tiprack_300 = protocol.load_labware ('vwr_96_tiprack_300ul', '3')
    reservoir = protocol.load_labware ('agilent_12_reservoir_21ml', '9')
    agarplate_1 = protocol.load_labware ('agarplate_96_wellplate_5ul', '1')

    # load pipettes
    p20multi = protocol.load_instrument ('p20_multi_gen2', 'right', tip_racks = [tiprack_20])
    
    # pipette for heat-shock transformation only (install before starting)
    p300multi = protocol.load_instrument ('p300_multi_gen2', 'left', tip_racks=[tiprack_300])

    # define variables
    column_list = ['1', '2', '3', '4', '5', '6','7', '8', '9', '10', '11', '12']

    # cooling of Thermocycler Module
    tc_mod.set_block_temperature(0)
    protocol.pause('Place a PCR plate containing 20 µl competent cells per well into the Thermocycler Module. Make sure that cells and DNA are thawed.')

    # transfer DNA into pcr plate with competent cells inside the Thermocycler Module
    p20multi.transfer (2, [DNA_plate.columns_by_name ()[column_name] for column_name in column_list],[tc_plate.columns_by_name ()[column_name] for column_name in column_list], mix_after = (5, 20), new_tip = 'always', blow_out = True, blowout_location='destination well' )
