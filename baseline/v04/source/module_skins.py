from header_skins import *
from ID_particle_systems import *
####################################################################################################################
#  Each skin record contains the following fields:
#  1) Skin id: used for referencing skins.
#  2) Skin flags. Not used yet. Should be 0.
#  3) Body mesh.
#  4) Calf mesh (left one).
#  5) Hand mesh (left one).
#  6) Head mesh.
#  7) Face keys (list)
#  8) List of hair meshes.
#  9) List of beard meshes.
# 10) List of hair textures.
# 11) List of beard textures.
# 12) List of face textures.
# 13) List of voices.
# 14) Skeleton name
# 15) Scale (doesn't fully work yet)
# 16) Blood particles 1 (do not add this if you wish to use the default particles)
# 17) Blood particles 2 (do not add this if you wish to use the default particles)
# 17) Face key constraints (do not add this if you do not wish to use it)
####################################################################################################################

# FewerBandits v3: man face keys from Virake's skins.txt (numbers match the pack's male_head mesh morphs)
man_face_keys = [
(240,0,-0.4,0.3, "Chin Size"),
(230,0,-0.4,0.8, "Chin Shape"),
(250,0,-0.25,0.55, "Chin Forward"),
(130,0,-0.5,1.0, "Jaw Width"),
(120,0,-0.5,0.6, "Lower Lip"),
(110,0,-0.2,0.6, "Upper Lip"),
(100,0,0.2,-0.2, "Mouth-Nose Distance"),
(90,0,0.55,-0.55, "Mouth Width"),
(30,0,-0.3,0.3, "Nostril Size"),
(60,0,0.25,-0.25, "Nose Height"),
(40,0,-0.2,0.3, "Nose Width"),
(70,0,-0.3,0.4, "Nose Size"),
(50,0,0.2,-0.3, "Nose Shape"),
(80,0,-0.3,0.65, "Nose Bridge"),
(160,0,-0.2,0.25, "Eye Width"),
(190,0,-0.25,0.15, "Eye to Eye Dist"),
(170,0,-0.85,0.85, "Eye Shape"),
(200,0,-0.3,0.7, "Eye Depth"),
(180,0,-1.5,1.5, "Eyelids"),
(20,0,0.6,-0.25, "Cheeks"),
(260,0,-0.6,0.5, "Cheek Bones"),
(220,0,0.8,-0.8, "Eyebrow Height"),
(210,0,-0.75,0.75, "Eyebrow Shape"),
(10,0,-0.6,0.5, "Temple Width"),
(270,0,-0.3,1.0, "Face Depth"),
(150,0,-0.25,0.45, "Face Ratio"),
(140,0,-0.4,0.5, "Face Width"),
(280,0,1.0,1.0, "Post-Edit"),
]
# Face width-Jaw width Temple width
# FewerBandits v3: woman face keys from Virake's skins.txt (pack's corprus_female_head mesh has only 4 morph keys)
woman_face_keys = [
(40,0,-1.0,0.0, "Caucassian 2"),
(30,0,0.0,1.0, "Caucassian 1"),
(10,0,0.0,1.0, "Forehead"),
(280,0,0.0,1.0, "Post-Edit"),
]
undead_face_keys = []


chin_size = 0
chin_shape = 1
chin_forward = 2
jaw_width = 3
jaw_position = 4
mouth_nose_distance = 5
mouth_width = 6
cheeks = 7
nose_height = 8
nose_width = 9
nose_size = 10
nose_shape = 11
nose_bridge = 12
cheek_bones = 13
eye_width = 14
eye_to_eye_dist = 15
eye_shape = 16
eye_depth = 17
eyelids = 18
eyebrow_position = 19
eyebrow_height = 20
eyebrow_depth = 21
eyebrow_shape = 22
temple_width = 23
face_depth = 24
face_ratio = 25
face_width = 26

comp_less_than = -1;
comp_greater_than = 1;

skins = [
  (
    "man", 0,
    "man_body", "man_calf_l", "m_handL",
    "male_head", man_face_keys,
    ["man_hair_s","man_hair_m","man_hair_n","man_hair_o", "man_hair_y10", "man_hair_y12","man_hair_p","man_hair_r","man_hair_q","man_hair_v","man_hair_t","man_hair_y6","man_hair_y3","man_hair_y7","man_hair_y9","man_hair_y11","man_hair_u","man_hair_y","man_hair_y2","man_hair_y4"], #man_hair_meshes ,"man_hair_y5","man_hair_y8",
    ["beard_e","beard_d","beard_k","beard_l","beard_i","beard_j","beard_z","beard_m","beard_n","beard_y","beard_p","beard_o",   "beard_v", "beard_f", "beard_b", "beard_c","beard_t","beard_u","beard_r","beard_s","beard_a","beard_h","beard_g",], #beard meshes ,"beard_q"
    ["hair_blonde", "hair_red", "hair_brunette", "hair_black", "hair_white"], #hair textures
    ["beard_blonde","beard_red","beard_brunette","beard_black","beard_white"], #beard_materials
    # FewerBandits v3: man face textures from Virake's skins.txt (20 faces)
    [("manface_young_2",0xffcbe0e0,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff502a19]),
     ("manface_midage",0xffdfefe1,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff632e18, 0xff502a19, 0xff19100c]),
     ("manface_young",0xffd0e0e0,["hair_blonde"],[0xff83301a, 0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("manface_young_3",0xffdceded,["hair_blonde"],[0xff2f180e, 0xff171313, 0xff007080c]),
     ("manface_7",0xffc0c8c8,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_midage_2",0xfde4c8d8,["hair_blonde"],[0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("manface_rugged",0xffb0aab5,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_asian1",0xffe3e8e1,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_asian2",0xffe3e8e1,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_asian3",0xffbbb6ae,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_mideast1",0xffaeb0a6,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_mideast2",0xffd0c8c1,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_mideast3",0xffe0e8e8,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_black1",0xff87655c,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_black2",0xff5a342d,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_black3",0xff634d3e,["hair_blonde"],[0xff171313, 0xff007080c]),
     ("manface_white1",0xffe0e8e8,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff632e18, 0xff502a19, 0xff19100c]),
     ("manface_white2",0xffe0e8e8,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff632e18, 0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("manface_white3",0xffe0e8e8,["hair_blonde"],[0xff83301a, 0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("manface_african",0xff807c8a,["hair_blonde"],[0xff120808, 0xff007080c]),
     ], #man_face_textures,
    [(voice_die,"snd_man_die"),(voice_hit,"snd_man_hit"),(voice_grunt,"snd_man_grunt"),(voice_grunt_long,"snd_man_grunt_long"),(voice_yell,"snd_man_yell"),(voice_stun,"snd_man_stun"),(voice_victory,"snd_man_victory")], #voice sounds
    "skel_human", 1.0,
    psys_game_blood,psys_game_blood_2,
    # FewerBandits v3: face-key constraints from Virake's skins.txt (indices match the pack's key list)
    [
     [1.6, comp_greater_than, (1.0,15), (1.0,23)],
     [0.6, comp_less_than, (1.0,15), (1.0,23)],
     [1.5, comp_greater_than, (1.0,25), (1.0,6)],
     [0.6, comp_greater_than, (-1.0,9), (1.0,6)],
     [-1.0, comp_less_than, (-1.0,9), (1.0,6)],
     ]
  ),
  
  (
    "woman", skf_use_morph_key_10,
    "woman_body",  "woman_calf_l", "f_handL",
    "corprus_female_head", woman_face_keys, # FewerBandits v3: pack head mesh (female_head is in the removed meshes_face_gen)
    ["woman_hair_p","woman_hair_n","woman_hair_o","woman_hair_q","woman_hair_l","woman_hair_t","woman_hair_s"], #woman_hair_meshes # FewerBandits v3: woman_hair_r is not in the pack (use woman_hair_l)
#    ["woman_hair_a","woman_hair_b","woman_hair_c","woman_hair_d","woman_hair_e","woman_hair_f","woman_hair_g"], #woman_hair_meshes
    [],
    ["hair_blonde", "hair_red", "hair_brunette", "hair_black", "hair_white"], #hair textures
    [],
    # FewerBandits v3: woman face textures from Virake's skins.txt (6 faces, _gaolu)
    [("womanface_young_gaolu",0xffe3e8ef,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff502a19, 0xff19100c]),
     ("womanface_b_gaolu",0xffdfdfdf,["hair_blonde"],[0xffa5481f, 0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("womanface_caucas_gaolu",0xffe8dfe5,["hair_blonde"],[0xff502a19, 0xff19100c, 0xff0c0d19]),
     ("womanface_brown_gaolu",0xffaf9f7e,["hair_blonde"],[0xff19100c, 0xff0c0d19, 0xff007080c]),
     ("womanface_african_gaolu",0xff808080,["hair_blonde"],[0xff120808, 0xff007080c]),
     ("womanface_c_gaolu",0xffe3e8ef,["hair_blonde"],[0xffffffff, 0xffb04717, 0xff502a19, 0xff19100c]),
     ],#woman_face_textures
    [(voice_die,"snd_woman_die"),(voice_hit,"snd_woman_hit"),(voice_yell,"snd_woman_yell")], #voice sounds
    "skel_human", 0.95, # FewerBandits v3: pack scale
    psys_game_blood,psys_game_blood_2,
  ),
  
##  (
##    "undead", 0,
##    "undead_body", "undead_calf_l", "undead_handL",
##    "undead_head", undead_face_keys,
##    [],
##    [],
##    [],
##    [],
##    [("undeadface_a",0xffffffff,[]),
##     ("undeadface_b",0xffcaffc0,[]),
##     ], #undead_face_textures
##    [], #voice sounds
##    "skel_human", 1.0,
##  ),
]

