from opentrons import protocol_api

metadata = {
    'protocolName': 'golden_gate_assembly',
    'author': 'Carolin Müller, Vera Waffenschnmidt',
    'description': 'Protocol for Golden Gate assembly using the Opentrons OT-2 with Thermocycler Module.',
    'apiLevel': '2.2'}

def run(protocol: protocol_api.ProtocolContext):
    
    # load module
    tc_mod = protocol.load_module('Thermocycler Module')

    # load labware, adjust if necessary
    plate = tc_mod.load_labware('biorad_96_wellplate_200ul_pcr')

    # maximum volume of wells 
    Vmax = 20

    tc_mod.set_lid_temperature(40)
    tc_mod.open_lid()
    protocol.pause('Insert PCR plate into thermocycler. Proceed, if done')
    tc_mod.close_lid()

    # temperature profile for Golden Gate assembly, adjust if necessary
    profile = [
        {'temperature': 37, 'hold_time_minutes': 1},
        {'temperature': 16, 'hold_time_minutes': 5}]
    
    tc_mod.execute_profile(steps=profile, repetitions=30, block_max_volume=Vmax) 
    tc_mod.set_block_temperature(37, hold_time_minutes=10, block_max_volume=Vmax)
    
    # enzyme inactivation, adjust if necessary
    tc_mod.set_lid_temperature(85)    
    tc_mod.set_block_temperature(80, hold_time_minutes=20, block_max_volume=Vmax) 
    
    # hold temperature until plate is removed
    tc_mod.deactivate_lid()
    tc_mod.set_block_temperature(0) 
    
    
