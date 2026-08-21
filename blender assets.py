import bpy
import os

# GitHub Actions Output Directory
PROJECT_ROOT = os.path.abspath("output_models/assets/models/")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)

def apply_white_material(obj):
    mat = bpy.data.materials.new(name="M_PlainWhite_Base")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
        bsdf.inputs['Metallic'].default_value = 0.0
    obj.data.materials.append(mat)

def export_glb(filepath):
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=True,
        export_draco_mesh_compression_enable=True
    )

def gen_box(dims, bevel_w=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.scale = dims
    bpy.ops.object.transform_apply(scale=True)
    if bevel_w > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel_w
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier="Bevel")
    apply_white_material(obj)
    return obj

def gen_cylinder(radius, depth, vertices=24, taper=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices)
    obj = bpy.context.active_object
    if taper != 1.0:
        for v in obj.data.vertices:
            if v.co.z > 0:
                v.co.x *= taper
                v.co.y *= taper
        obj.data.update()
    apply_white_material(obj)
    return obj

def gen_sphere(radius, subdivisions=3, squish=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, subdivisions=subdivisions)
    obj = bpy.context.active_object
    obj.scale = squish
    bpy.ops.object.transform_apply(scale=True)
    apply_white_material(obj)
    return obj

def gen_capsule(radius, length):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=16, ring_count=8)
    obj = bpy.context.active_object
    obj.scale = (1.0, 1.0, length / (radius * 2.0))
    bpy.ops.object.transform_apply(scale=True)
    apply_white_material(obj)
    return obj

def gen_torus(major_r, minor_r):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r)
    obj = bpy.context.active_object
    apply_white_material(obj)
    return obj

def gen_pipe(radius, depth, thickness=0.04):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=20)
    obj = bpy.context.active_object
    mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = thickness
    bpy.ops.object.modifier_apply(modifier="Solidify")
    apply_white_material(obj)
    return obj

def gen_cone(radius, depth, vertices=20):
    bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=depth, vertices=vertices)
    obj = bpy.context.active_object
    apply_white_material(obj)
    return obj

def gen_hollow_bowl(radius, thickness=0.05):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=12)
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_outer=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = thickness
    bpy.ops.object.modifier_apply(modifier="Solidify")
    apply_white_material(obj)
    return obj

MODEL_REGISTRY = {
    ("base_shells", "shell_wall_3x3_plain.glb"): ("box", ((3.0, 0.2, 3.0), 0.05)),
    ("base_shells", "shell_wall_3x3_window_hole.glb"): ("box", ((3.0, 0.2, 3.0), 0.02)),
    ("base_shells", "shell_wall_3x3_door_arch.glb"): ("box", ((3.0, 0.2, 3.0), 0.02)),
    ("base_shells", "shell_wall_curve_corner.glb"): ("cylinder", (1.5, 3.0, 16, 1.0)),
    ("base_shells", "shell_foundation_slab_3x3.glb"): ("box", ((3.0, 3.0, 0.4), 0.03)),
    ("base_shells", "shell_foundation_stilt_wood.glb"): ("box", ((3.0, 3.0, 1.5), 0.05)),
    ("base_shells", "shell_foundation_metal_grid.glb"): ("box", ((3.0, 3.0, 0.1), 0.01)),
    ("base_shells", "shell_roof_slope_45.glb"): ("box", ((3.0, 2.2, 0.15), 0.02)),
    ("base_shells", "shell_roof_slope_corner.glb"): ("cone", (2.0, 1.5, 4)),
    ("base_shells", "shell_roof_flat_slab.glb"): ("box", ((3.0, 3.0, 0.15), 0.02)),
    ("base_shells", "shell_roof_dome_frame.glb"): ("hollow_bowl", (1.8, 0.08)),
    ("base_shells", "shell_door_frame_single.glb"): ("box", ((1.2, 0.2, 2.2), 0.02)),
    ("base_shells", "shell_door_frame_double.glb"): ("box", ((2.4, 0.2, 2.2), 0.02)),
    ("base_shells", "shell_gate_security_frame.glb"): ("box", ((3.5, 0.4, 3.0), 0.08)),
    ("base_shells", "shell_stairs_straight.glb"): ("box", ((1.2, 3.0, 3.0), 0.0)),
    ("base_shells", "shell_stairs_spiral.glb"): ("cylinder", (1.2, 3.0, 12, 1.0)),
    ("base_shells", "shell_ladder_vertical.glb"): ("box", ((0.6, 0.1, 3.0), 0.01)),
    ("base_shells", "shell_ramp_vehicle.glb"): ("box", ((3.0, 6.0, 1.0), 0.0)),
    ("base_shells", "shell_beam_i_truss.glb"): ("box", ((0.3, 3.0, 0.3), 0.02)),
    ("base_shells", "shell_pillar_round_column.glb"): ("cylinder", (0.3, 3.0, 20, 1.0)),
    ("base_shells", "shell_chest_cap_left.glb"): ("box", ((0.5, 0.8, 0.6), 0.04)),
    ("base_shells", "shell_chest_mid_segment.glb"): ("box", ((1.0, 0.8, 0.6), 0.04)),
    ("base_shells", "shell_chest_cap_right.glb"): ("box", ((0.5, 0.8, 0.6), 0.04)),
    ("base_shells", "shell_safe_heavy_cube.glb"): ("box", ((1.0, 1.0, 1.0), 0.06)),
    ("base_shells", "shell_coffin_oak.glb"): ("box", ((0.8, 2.0, 0.5), 0.04)),
    ("base_shells", "shell_locker_tall.glb"): ("box", ((0.6, 0.6, 2.0), 0.03)),
    ("base_shells", "shell_bed_frame_single.glb"): ("box", ((1.0, 2.0, 0.4), 0.03)),
    ("base_shells", "shell_bed_frame_double.glb"): ("box", ((2.0, 2.0, 0.4), 0.03)),
    ("base_shells", "shell_medical_cot_frame.glb"): ("box", ((0.9, 2.1, 0.6), 0.02)),
    ("base_shells", "shell_chair_wooden_frame.glb"): ("box", ((0.5, 0.5, 0.9), 0.02)),
    ("base_shells", "shell_sofa_base_couch.glb"): ("box", ((2.2, 0.9, 0.8), 0.08)),
    ("base_shells", "shell_bar_stool_frame.glb"): ("cylinder", (0.25, 0.9, 16, 1.0)),
    ("base_shells", "shell_table_dining_frame.glb"): ("box", ((2.0, 1.0, 0.75), 0.03)),
    ("base_shells", "shell_desk_command_terminal.glb"): ("box", ((2.2, 1.2, 0.8), 0.05)),
    ("base_shells", "shell_bookshelf_frame.glb"): ("box", ((1.2, 0.4, 2.0), 0.02)),
    ("base_shells", "shell_display_cabinet_frame.glb"): ("box", ((1.0, 0.5, 1.9), 0.03)),
    ("base_shells", "shell_toilet_porcelain_base.glb"): ("box", ((0.5, 0.7, 0.8), 0.08)),
    ("base_shells", "shell_sink_basin_counter.glb"): ("box", ((0.8, 0.6, 0.85), 0.04)),
    ("base_shells", "shell_bathtub_basin.glb"): ("box", ((0.9, 1.8, 0.6), 0.1)),
    ("base_shells", "shell_cooking_stove_frame.glb"): ("box", ((0.8, 0.8, 0.9), 0.03)),
    ("base_shells", "shell_chassis_buggy_light.glb"): ("box", ((1.6, 3.0, 0.6), 0.05)),
    ("base_shells", "shell_chassis_rover_heavy_mid.glb"): ("box", ((2.4, 4.5, 0.9), 0.08)),
    ("base_shells", "shell_chassis_crawler_6x6.glb"): ("box", ((2.6, 6.0, 1.1), 0.1)),
    ("base_shells", "shell_chassis_rocket_wheelchair.glb"): ("box", ((0.8, 1.1, 1.0), 0.04)),
    ("base_shells", "shell_chassis_hoverbike.glb"): ("capsule", (0.4, 2.2)),
    ("base_shells", "shell_chassis_air_skiff.glb"): ("box", ((2.0, 5.0, 0.8), 0.1)),
    ("base_shells", "shell_chassis_submersible.glb"): ("capsule", (0.9, 4.0)),
    ("base_shells", "shell_van_transit_12seater.glb"): ("box", ((2.2, 5.5, 2.2), 0.12)),
    ("base_shells", "shell_shopping_cart_frame.glb"): ("box", ((0.6, 0.9, 0.9), 0.02)),
    ("base_shells", "shell_cockpit_rollcage.glb"): ("box", ((1.4, 1.4, 1.2), 0.02)),
    ("base_shells", "shell_cockpit_armored_pod.glb"): ("box", ((1.5, 1.6, 1.3), 0.08)),
    ("base_shells", "shell_trailer_hitch_flatbed.glb"): ("box", ((2.0, 3.5, 0.3), 0.02)),
    ("base_shells", "shell_airplane_fuselage_cabin.glb"): ("capsule", (1.2, 12.0)),
    ("base_shells", "shell_airplane_wing_main.glb"): ("box", ((14.0, 1.8, 0.15), 0.02)),
    ("base_shells", "shell_airplane_tail_rudder.glb"): ("box", ((0.15, 1.2, 2.0), 0.02)),
    ("base_shells", "shell_drill_rig_frame.glb"): ("box", ((1.5, 1.5, 3.5), 0.05)),
    ("base_shells", "shell_pump_housing.glb"): ("cylinder", (0.5, 0.8, 18, 1.0)),
    ("base_shells", "shell_smelter_kiln_blast.glb"): ("cylinder", (0.9, 2.2, 20, 0.8)),
    ("base_shells", "shell_crusher_hopper.glb"): ("cone", (1.0, 1.4, 4)),
    ("base_shells", "shell_fabricator_3d_frame.glb"): ("box", ((1.4, 1.4, 1.6), 0.04)),
    ("base_shells", "shell_assembler_robotic_bed.glb"): ("box", ((2.0, 2.0, 0.8), 0.05)),
    ("base_shells", "shell_cloning_vat_industrial.glb"): ("cylinder", (0.7, 2.4, 24, 1.0)),
    ("base_shells", "shell_conveyor_straight_1m.glb"): ("box", ((0.8, 1.0, 0.3), 0.02)),
    ("base_shells", "shell_conveyor_corner_90.glb"): ("cylinder", (0.8, 0.3, 12, 1.0)),
    ("base_shells", "shell_pipe_segment_2m.glb"): ("pipe", (0.2, 2.0, 0.03)),
    ("base_shells", "shell_pipe_t_junction.glb"): ("box", ((0.5, 0.5, 0.5), 0.02)),
    ("base_shells", "shell_solar_stand_tracker.glb"): ("cylinder", (0.15, 1.4, 12, 1.0)),
    ("base_shells", "shell_wind_turbine_tower.glb"): ("cylinder", (0.4, 12.0, 16, 0.5)),
    ("base_shells", "shell_generator_combustion_block.glb"): ("box", ((1.2, 1.8, 1.1), 0.06)),
    ("base_shells", "shell_battery_rack_housing.glb"): ("box", ((1.0, 0.8, 1.8), 0.04)),
    ("base_shells", "shell_receiver_pistol.glb"): ("box", ((0.08, 0.22, 0.15), 0.01)),
    ("base_shells", "shell_receiver_rifle_kinetic.glb"): ("box", ((0.1, 0.55, 0.2), 0.02)),
    ("base_shells", "shell_receiver_plasma_cannon.glb"): ("box", ((0.2, 0.7, 0.3), 0.03)),
    ("base_shells", "shell_receiver_shotgun.glb"): ("box", ((0.1, 0.6, 0.18), 0.02)),
    ("base_shells", "shell_receiver_rocket_launcher.glb"): ("pipe", (0.15, 1.2, 0.02)),
    ("base_shells", "shell_receiver_emp_grenade_launcher.glb"): ("cylinder", (0.18, 0.6, 16, 1.0)),
    ("base_shells", "shell_receiver_glitch_gun.glb"): ("box", ((0.12, 0.45, 0.22), 0.03)),
    ("base_shells", "shell_hilt_sword_onehand.glb"): ("cylinder", (0.025, 0.25, 12, 1.0)),
    ("base_shells", "shell_hilt_sword_twohand.glb"): ("cylinder", (0.03, 0.45, 12, 1.0)),
    ("base_shells", "shell_hilt_dagger.glb"): ("cylinder", (0.02, 0.16, 12, 1.0)),
    ("base_shells", "shell_shaft_spear_pole.glb"): ("cylinder", (0.025, 2.0, 12, 1.0)),
    ("base_shells", "shell_handle_pickaxe.glb"): ("cylinder", (0.03, 0.85, 12, 0.9)),
    ("base_shells", "shell_handle_axe.glb"): ("cylinder", (0.03, 0.75, 12, 0.9)),
    ("base_shells", "shell_handle_welder.glb"): ("cylinder", (0.035, 0.3, 12, 1.0)),
    ("base_shells", "shell_frame_creator_wand.glb"): ("cylinder", (0.02, 0.5, 16, 1.2)),
    ("modular_props", "prop_tap_brass_sink.glb"): ("pipe", (0.03, 0.35, 0.005)),
    ("modular_props", "prop_tap_wall_spigot.glb"): ("cylinder", (0.04, 0.15, 12, 1.0)),
    ("modular_props", "prop_tap_sensor_chrome.glb"): ("box", ((0.06, 0.15, 0.2), 0.01)),
    ("modular_props", "prop_tap_showerhead.glb"): ("cylinder", (0.15, 0.04, 20, 1.0)),
    ("modular_props", "prop_valve_wheel_red.glb"): ("torus", (0.12, 0.02)),
    ("modular_props", "prop_valve_lever_quarter_turn.glb"): ("box", ((0.03, 0.18, 0.02), 0.005)),
    ("modular_props", "prop_valve_pressure_emergency.glb"): ("cylinder", (0.06, 0.2, 16, 1.0)),
    ("modular_props", "prop_pressure_gauge_dial.glb"): ("cylinder", (0.08, 0.03, 20, 1.0)),
    ("modular_props", "prop_pipe_flange_connector.glb"): ("torus", (0.22, 0.03)),
    ("modular_props", "prop_tank_500l_rooftop.glb"): ("cylinder", (0.6, 1.2, 20, 1.0)),
    ("modular_props", "prop_faucet_gold_luxury.glb"): ("pipe", (0.035, 0.4, 0.005)),
    ("modular_props", "prop_hose_garden_spigot.glb"): ("torus", (0.25, 0.08)),
    ("modular_props", "prop_water_nozzle_spray.glb"): ("cone", (0.04, 0.2, 12)),
    ("modular_props", "prop_siphon_filter_mesh.glb"): ("cylinder", (0.1, 0.25, 16, 1.0)),
    ("modular_props", "prop_drain_grate_iron.glb"): ("box", ((0.2, 0.2, 0.02), 0.005)),
    ("modular_props", "prop_padlock_iron.glb"): ("box", ((0.08, 0.04, 0.1), 0.01)),
    ("modular_props", "prop_keypad_digital_pin.glb"): ("box", ((0.12, 0.03, 0.18), 0.01)),
    ("modular_props", "prop_scanner_biometric_thumb.glb"): ("box", ((0.1, 0.04, 0.14), 0.01)),
    ("modular_props", "prop_latch_deadbolt.glb"): ("cylinder", (0.02, 0.15, 12, 1.0)),
    ("modular_props", "prop_bracket_corner_reinforced.glb"): ("box", ((0.15, 0.15, 0.15), 0.01)),
    ("modular_props", "prop_bracket_hinge_heavy.glb"): ("cylinder", (0.02, 0.12, 12, 1.0)),
    ("modular_props", "prop_handle_drawer_pull.glb"): ("torus", (0.06, 0.01)),
    ("modular_props", "prop_plate_steel_armor.glb"): ("box", ((0.8, 0.8, 0.04), 0.005)),
    ("modular_props", "prop_door_slab_wood_solid.glb"): ("box", ((1.0, 0.08, 2.0), 0.01)),
    ("modular_props", "prop_door_slab_glass_window.glb"): ("box", ((1.0, 0.04, 2.0), 0.005)),
    ("modular_props", "prop_door_slab_airlock_blast.glb"): ("box", ((1.2, 0.15, 2.2), 0.03)),
    ("modular_props", "prop_window_iron_bars.glb"): ("box", ((1.0, 0.05, 1.0), 0.01)),
    ("modular_props", "prop_spikes_defense_iron.glb"): ("cone", (0.15, 0.6, 8)),
    ("modular_props", "prop_barbed_wire_coil.glb"): ("torus", (0.35, 0.04)),
    ("modular_props", "prop_debris_chunk_metal.glb"): ("sphere", (0.2, 2, (1.2, 0.8, 1.0))),
    ("modular_props", "prop_debris_chunk_stone.glb"): ("sphere", (0.25, 2, (1.0, 1.3, 0.7))),
    ("modular_props", "prop_toilet_paper_roll.glb"): ("pipe", (0.08, 0.12, 0.03)),
    ("modular_props", "prop_shattered_ceramic_shards.glb"): ("sphere", (0.15, 2, (1.5, 0.5, 1.0))),
    ("modular_props", "prop_straw_bedding_mat.glb"): ("box", ((0.9, 1.8, 0.08), 0.02)),
    ("modular_props", "prop_pillow_comfort.glb"): ("sphere", (0.3, 3, (1.4, 1.0, 0.5))),
    ("modular_props", "prop_wheel_offroad_tread.glb"): ("cylinder", (0.55, 0.35, 20, 1.0)),
    ("modular_props", "prop_wheel_racing_slick.glb"): ("cylinder", (0.45, 0.3, 24, 1.0)),
    ("modular_props", "prop_wheel_metal_wagon.glb"): ("cylinder", (0.6, 0.1, 16, 1.0)),
    ("modular_props", "prop_tread_tank_belt.glb"): ("box", ((0.5, 2.2, 0.6), 0.08)),
    ("modular_props", "prop_thruster_hover_ion.glb"): ("cylinder", (0.35, 0.25, 18, 0.8)),
    ("modular_props", "prop_thruster_rocket_solid.glb"): ("cone", (0.3, 0.8, 18)),
    ("modular_props", "prop_thruster_jet_intake.glb"): ("cylinder", (0.4, 0.9, 20, 1.1)),
    ("modular_props", "prop_skid_rocket_steel.glb"): ("box", ((0.15, 1.8, 0.05), 0.01)),
    ("modular_props", "prop_engine_v8_combustion.glb"): ("box", ((0.8, 0.9, 0.7), 0.04)),
    ("modular_props", "prop_engine_plasma_core.glb"): ("sphere", (0.45, 3, (1.0, 1.0, 1.0))),
    ("modular_props", "prop_engine_solar_hybrid.glb"): ("cylinder", (0.35, 0.7, 16, 1.0)),
    ("modular_props", "prop_radiator_cooling_grille.glb"): ("box", ((0.8, 0.1, 0.6), 0.01)),
    ("modular_props", "prop_headlight_pair_halogen.glb"): ("cylinder", (0.12, 0.08, 16, 1.0)),
    ("modular_props", "prop_headlight_pair_neon.glb"): ("box", ((0.9, 0.06, 0.06), 0.01)),
    ("modular_props", "prop_bumper_ram_heavy.glb"): ("pipe", (0.08, 2.0, 0.02)),
    ("modular_props", "prop_exhaust_pipe_dual.glb"): ("pipe", (0.06, 0.9, 0.01)),
    ("modular_props", "prop_windshield_curved_glass.glb"): ("sphere", (0.8, 3, (1.4, 0.6, 0.8))),
    ("modular_props", "prop_windshield_armored_slits.glb"): ("box", ((1.4, 0.08, 0.6), 0.02)),
    ("modular_props", "prop_vehicle_mining_drill_bit.glb"): ("cone", (0.4, 1.1, 16)),
    ("modular_props", "prop_radio_antenna_whip.glb"): ("cylinder", (0.01, 2.5, 8, 0.5)),
    ("modular_props", "prop_barrel_standard_rifled.glb"): ("pipe", (0.03, 0.5, 0.008)),
    ("modular_props", "prop_barrel_plasma_wide.glb"): ("pipe", (0.06, 0.6, 0.015)),
    ("modular_props", "prop_barrel_sniper_long.glb"): ("pipe", (0.025, 0.85, 0.008)),
    ("modular_props", "prop_barrel_shotgun_quad.glb"): ("cylinder", (0.06, 0.5, 12, 1.0)),
    ("modular_props", "prop_scope_2x_red_dot.glb"): ("cylinder", (0.035, 0.14, 16, 1.0)),
    ("modular_props", "prop_scope_4x_optical.glb"): ("cylinder", (0.04, 0.3, 16, 1.2)),
    ("modular_props", "prop_scope_thermal_sensor.glb"): ("box", ((0.08, 0.22, 0.09), 0.01)),
    ("modular_props", "prop_laser_pointer_rail.glb"): ("box", ((0.03, 0.08, 0.03), 0.005)),
    ("modular_props", "prop_stock_wood_classic.glb"): ("box", ((0.06, 0.35, 0.14), 0.02)),
    ("modular_props", "prop_stock_tactical_foldable.glb"): ("pipe", (0.02, 0.3, 0.005)),
    ("modular_props", "prop_stock_heavy_recoil_pad.glb"): ("box", ((0.08, 0.28, 0.16), 0.03)),
    ("modular_props", "prop_grip_foregrip_vertical.glb"): ("cylinder", (0.025, 0.14, 12, 1.0)),
    ("modular_props", "prop_blade_magma_edge.glb"): ("box", ((0.04, 0.8, 0.08), 0.01)),
    ("modular_props", "prop_blade_steel_katana.glb"): ("box", ((0.02, 0.9, 0.06), 0.005)),
    ("modular_props", "prop_blade_plasma_energy.glb"): ("capsule", (0.03, 0.85)),
    ("modular_props", "prop_blade_dagger_curved.glb"): ("cone", (0.03, 0.35, 12)),
    ("modular_props", "prop_head_warhammer_blunt.glb"): ("box", ((0.18, 0.22, 0.18), 0.02)),
    ("modular_props", "prop_tip_spear_trident.glb"): ("cone", (0.1, 0.45, 8)),
    ("modular_props", "prop_pommel_crystal_counterweight.glb"): ("sphere", (0.04, 2, (1.0, 1.0, 1.0))),
    ("modular_props", "prop_crossguard_winged.glb"): ("box", ((0.28, 0.04, 0.04), 0.01)),
    ("modular_props", "prop_crt_screen_tv.glb"): ("box", ((0.4, 0.3, 0.3), 0.03)),
    ("modular_props", "prop_camera_broadcast_studio.glb"): ("box", ((0.25, 0.45, 0.3), 0.02)),
    ("modular_props", "prop_antenna_satellite_dish.glb"): ("hollow_bowl", (0.75, 0.02)),
    ("modular_props", "prop_speaker_horn_siren.glb"): ("cone", (0.25, 0.4, 16)),
    ("modular_props", "prop_sensor_motion_infra.glb"): ("sphere", (0.06, 3, (1.0, 1.0, 0.5))),
    ("modular_props", "prop_sensor_light_daylight.glb"): ("cylinder", (0.04, 0.06, 12, 1.0)),
    ("modular_props", "prop_sensor_pressure_plate.glb"): ("box", ((0.5, 0.5, 0.03), 0.005)),
    ("modular_props", "prop_laser_tripwire_emitter.glb"): ("cylinder", (0.03, 0.08, 12, 1.0)),
    ("modular_props", "prop_logic_node_gate_box.glb"): ("box", ((0.15, 0.15, 0.08), 0.01)),
    ("modular_props", "prop_solar_panel_glass_sheet.glb"): ("box", ((1.0, 1.8, 0.03), 0.005)),
    ("modular_props", "prop_battery_cell_100kwh.glb"): ("box", ((0.3, 0.4, 0.6), 0.02)),
    ("modular_props", "prop_power_pole_crossarm.glb"): ("box", ((2.2, 0.15, 0.15), 0.01)),
    ("modular_props", "prop_breaker_box_lever.glb"): ("box", ((0.25, 0.12, 0.35), 0.01)),
    ("modular_props", "prop_transformer_stepdown.glb"): ("cylinder", (0.3, 0.8, 16, 1.0)),
    ("modular_props", "prop_beacon_light_rotary.glb"): ("cylinder", (0.1, 0.15, 16, 0.9)),
    ("modular_props", "prop_led_status_bar.glb"): ("box", ((0.3, 0.02, 0.04), 0.002)),
    ("modular_props", "prop_inspection_snake_cam.glb"): ("cylinder", (0.015, 1.5, 8, 1.0)),
    ("modular_props", "prop_tablet_screen.glb"): ("box", ((0.2, 0.28, 0.01), 0.005)),
    ("modular_props", "prop_smartphone_handheld.glb"): ("box", ((0.075, 0.15, 0.008), 0.004)),
    ("modular_props", "prop_monocle_gold_eye.glb"): ("torus", (0.025, 0.003)),
    ("anatomy_parts", "part_head_human_male.glb"): ("sphere", (0.18, 3, (0.9, 1.1, 1.0))),
    ("anatomy_parts", "part_head_human_female.glb"): ("sphere", (0.16, 3, (0.85, 1.05, 0.95))),
    ("anatomy_parts", "part_head_elder_geezer.glb"): ("sphere", (0.19, 3, (0.95, 1.15, 1.05))),
    ("anatomy_parts", "part_head_tiger_saber.glb"): ("sphere", (0.24, 3, (1.2, 1.4, 1.1))),
    ("anatomy_parts", "part_head_wolf_canine.glb"): ("cone", (0.18, 0.45, 14)),
    ("a
