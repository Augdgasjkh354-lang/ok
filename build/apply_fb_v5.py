#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FewerBandits v5: buff all 16 companions + gather them in two taverns.
#
# 1. module_troops.py: every npc1-npc16 gets +5 levels, +2-3 str/agi,
#    +1-2 int/cha, main weapon proficiency 150-200, riding 4-5, role-fitting
#    combat skills, and a full kit (horse + melee weapon + shield / bow +
#    arrows + mid-high armor set). Skills are written out explicitly (no
#    knows_*_npc macros) so no skill level is ever OR-ed twice.
#    Faces (the 0x... line) are left untouched.
# 2. module_scripts.py (game_start): after the vanilla companion shuffle,
#    npc1-8 are placed in the player's starting town tavern, npc9-16 in the
#    nearest other town's tavern, and a message names both towns. The
#    starting town is $g_starting_town (set during character creation, before
#    game_start runs); fallback is Praven if it is somehow unset.
#    Why two towns, not one: Native tavern scenes only define ~9 visitor
#    entry points (16-24 per the TaleWorlds scene guide) and the tavern menu
#    spawns visitors from entry 17 upward; 16 companions in one tavern would
#    overflow the scene and the last ones (Klethi etc.) would silently never
#    appear. 8+8 keeps each tavern inside the vanilla visitor budget.
# 3. module_triggers.py: the 15-day reshuffle trigger
#    (script_update_companion_candidates_in_taverns every 24*15h) is disabled
#    (same treatment vanilla already gave the 72h trigger in
#    module_simple_triggers.py), so placed companions stay put. Dismissed
#    companions still move via the dialog code, as before.
# 4. module_strings.py: one new string (str_fb_companions_gathered) for the
#    game-start message. The file's coding is switched cp1254 -> utf-8 (it
#    is pure ASCII except two cp1254 dash bytes 0x96/0x97 in English flavor
#    text, normalized to "-" first; see below).
#
# Byte-level edits on CRLF files; every edit asserts its count.
import sys

B = "/home/hatch/workspace/warband-mod/build/"
CRLF = "\r\n"

def load(path):
    with open(path, "rb") as f:
        return f.read()

def save(path, data):
    with open(path, "wb") as f:
        f.write(data)

def replace(path, data, old, new, expect=1):
    old_b = old.encode("utf-8") if isinstance(old, str) else old
    new_b = new.encode("utf-8") if isinstance(new, str) else new
    n = data.count(old_b)
    assert n == expect, "%s: expected %d of %r, found %d" % (path, expect, old[:70], n)
    data = data.replace(old_b, new_b)
    print("OK %s: %d x %r" % (path, n, old[:70]))
    return data

def replace_npc_entry(path, data, tid, new_lines):
    """Replace the first 3 lines of a companion entry; keep the face line."""
    text = data.decode("utf-8")
    lines = text.split(CRLF)
    idx = None
    for i, ln in enumerate(lines):
        if ln.startswith('  ["%s",' % tid):
            idx = i
            break
    assert idx is not None, "%s: troop %s not found" % (path, tid)
    # sanity: we are on a vanilla-style entry (attribs/wp line, skills line)
    assert "level(" in lines[idx + 1] and "wp(" in lines[idx + 1], \
        "%s: %s line 2 unexpected: %r" % (path, tid, lines[idx + 1])
    assert "knows_" in lines[idx + 2], \
        "%s: %s line 3 unexpected: %r" % (path, tid, lines[idx + 2])
    face = lines[idx + 3]
    assert face.strip().startswith("0x") and face.rstrip().endswith("],"), \
        "%s: %s face line unexpected: %r" % (path, tid, face)
    lines[idx:idx + 3] = new_lines
    assert lines[idx + 3] == face, "%s: face line moved for %s" % (path, tid)
    print("OK %s: companion %s buffed" % (path, tid))
    return CRLF.join(lines).encode("utf-8")

T = B + "module_troops.py"
S = B + "module_scripts.py"
G = B + "module_triggers.py"
N = B + "module_strings.py"

# ---------------------------------------------------------------- 1. companions
# Current values read from module_troops.py before editing (level, str/agi/
# int/cha, wp, role): Borcha L3 8/7/12/7 wp60 tracker; Marnid L1 7/7/11/6
# wp40 merchant; Ymira L1 6/9/11/6 wp20 merchant/medic; Rolf L10 10/9/13/10
# wp110 warrior; Baheshtur L5 9/9/12/7 wp90 horse archer; Firentis L6
# 10/12/10/5 wp105 warrior; Deshavi L2 8/9/10/6 wp80 archer; Matheld L7
# 9/10/9/10 wp90 warrior; Alayen L2 11/8/7/8 wp100 warrior; Bunduk L9
# 12/8/9/11 wp105 crossbow; Katrin L8 8/11/10/10 wp70 merchant/warrior;
# Jeremus L4 8/7/13/7 wp30 medic; Nizar L3 7/7/12/8 wp80 cavalry; Lezalit
# L5 9/8/11/8 wp100 trainer; Artimenner L7 9/9/12/8 wp80 engineer; Klethi
# L2 7/11/8/7 wp80 thrower.
data = load(T)

# npc1 Borcha: tracker / horse archer. L3->8, bow 170, horse archery 4.
data = replace_npc_entry(T, data, "npc1", [
  "  # FewerBandits v5: tracker/horse archer, L8, bow 170, riding 5, full kit",
  '  ["npc1","Borcha","Borcha",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_scimitar,itm_khergit_bow,itm_khergit_arrows,itm_tab_shield_small_round_b,itm_khergit_guard_armor,itm_khergit_guard_helmet,itm_khergit_guard_boots,itm_lamellar_gauntlets,itm_courser],',
  '   str_10|agi_10|int_13|cha_8|level(8),wpex(160,100,130,170,90,120),knows_ironflesh_3|knows_power_strike_3|knows_power_draw_4|knows_horse_archery_4|knows_riding_5|knows_athletics_4|knows_weapon_master_3|knows_tracking_4|knows_pathfinding_4|knows_spotting_3|knows_shield_2|knows_inventory_management_2,',
])

# npc2 Marnid: merchant / swordsman. L1->6, one-handed 170.
data = replace_npc_entry(T, data, "npc2", [
  "  # FewerBandits v5: merchant/swordsman, L6, one-handed 170, trade 4",
  '  ["npc2","Marnid","Marnid", tf_hero|tf_unmoveable_in_party_window, 0,reserved, fac_commoners,[itm_sword_medieval_b,itm_tab_shield_heater_c,itm_mail_shirt,itm_kettle_hat,itm_leather_boots,itm_leather_gloves,itm_hunter],',
  '   str_9|agi_9|int_13|cha_8|level(6),wpex(170,110,110,90,90,90),knows_ironflesh_3|knows_power_strike_4|knows_riding_4|knows_athletics_3|knows_weapon_master_3|knows_shield_3|knows_trade_4|knows_inventory_management_4|knows_leadership_2|knows_first_aid_2|knows_wound_treatment_2,',
])

# npc3 Ymira: merchant / medic. L1->6, first aid 4, surgery 3.
data = replace_npc_entry(T, data, "npc3", [
  "  # FewerBandits v5: merchant/medic, L6, first aid 4, surgery 3",
  '  ["npc3","Ymira","Ymira",tf_female|tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_a,itm_tab_shield_small_round_b,itm_mail_shirt,itm_kettle_hat,itm_leather_boots,itm_leather_gloves,itm_hunter],',
  '   str_8|agi_11|int_13|cha_8|level(6),wpex(150,90,100,110,90,90),knows_ironflesh_2|knows_power_strike_3|knows_riding_4|knows_athletics_3|knows_weapon_master_2|knows_shield_3|knows_trade_3|knows_first_aid_4|knows_surgery_3|knows_wound_treatment_3|knows_inventory_management_3,',
])

# npc4 Rolf: heavy warrior. L10->15, one-handed 190, ironflesh 5.
data = replace_npc_entry(T, data, "npc4", [
  "  # FewerBandits v5: heavy warrior, L15, one-handed 190, power strike 5",
  '  ["npc4","Rolf","Rolf",tf_hero|tf_unmoveable_in_party_window, 0, reserved,  fac_commoners,[itm_sword_medieval_c,itm_tab_shield_heater_cav_a,itm_coat_of_plates_red,itm_guard_helmet,itm_plate_boots,itm_gauntlets,itm_warhorse],',
  '   str_12|agi_11|int_14|cha_11|level(15),wpex(190,170,150,90,90,130),knows_ironflesh_5|knows_power_strike_5|knows_power_throw_3|knows_riding_4|knows_athletics_5|knows_weapon_master_4|knows_shield_4|knows_tactics_3|knows_leadership_3|knows_first_aid_2|knows_surgery_2|knows_trainer_2,',
])

# npc5 Baheshtur: warrior / horse archer. L5->10, bow 170, horse archery 5.
data = replace_npc_entry(T, data, "npc5", [
  "  # FewerBandits v5: warrior/horse archer, L10, bow 170, horse archery 5",
  '  ["npc5","Baheshtur","Baheshtur",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_khergit_2,itm_khergit_bow,itm_khergit_arrows,itm_tab_shield_small_round_b,itm_khergit_guard_armor,itm_khergit_guard_helmet,itm_khergit_guard_boots,itm_lamellar_gauntlets,itm_courser],',
  '   str_11|agi_11|int_13|cha_9|level(10),wpex(170,110,140,170,90,120),knows_ironflesh_3|knows_power_strike_4|knows_power_draw_4|knows_horse_archery_5|knows_riding_5|knows_athletics_4|knows_weapon_master_3|knows_shield_2|knows_leadership_3,',
])

# npc6 Firentis: warrior. L6->11, one-handed 190, riding 5.
data = replace_npc_entry(T, data, "npc6", [
  "  # FewerBandits v5: warrior, L11, one-handed 190, riding 5",
  '  ["npc6","Firentis","Firentis",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_c,itm_tab_shield_heater_c,itm_plate_armor,itm_bascinet,itm_plate_boots,itm_gauntlets,itm_charger],',
  '   str_12|agi_14|int_11|cha_7|level(11),wpex(190,160,140,90,90,110),knows_ironflesh_4|knows_power_strike_5|knows_riding_5|knows_athletics_5|knows_weapon_master_4|knows_shield_4|knows_trainer_2|knows_leadership_2,',
])

# npc7 Deshavi: tracker / archer. L2->7, archery 190, power draw 5.
data = replace_npc_entry(T, data, "npc7", [
  "  # FewerBandits v5: tracker/archer, L7, archery 190, power draw 5",
  '  ["npc7","Deshavi","Deshavi",tf_female|tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_long_bow,itm_barbed_arrows,itm_sword_medieval_a,itm_tab_shield_small_round_b,itm_haubergeon,itm_kettle_hat,itm_leather_boots,itm_leather_gloves,itm_hunter],',
  '   str_10|agi_12|int_11|cha_8|level(7),wpex(150,100,110,190,90,110),knows_ironflesh_2|knows_power_strike_2|knows_power_draw_5|knows_riding_4|knows_athletics_4|knows_weapon_master_3|knows_tracking_4|knows_pathfinding_3|knows_spotting_4|knows_shield_2,',
])

# npc8 Matheld: warrior. L7->12, one-handed 190, shield 5.
data = replace_npc_entry(T, data, "npc8", [
  "  # FewerBandits v5: warrior, L12, one-handed 190, shield 5",
  '  ["npc8","Matheld","Matheld",tf_female|tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_viking_3_small,itm_tab_shield_round_e,itm_banded_armor,itm_nordic_huscarl_helmet,itm_mail_boots,itm_gauntlets,itm_hunter],',
  '   str_11|agi_12|int_10|cha_11|level(12),wpex(190,170,150,90,110,130),knows_ironflesh_4|knows_power_strike_5|knows_riding_4|knows_athletics_5|knows_weapon_master_4|knows_shield_5|knows_leadership_4|knows_tactics_2|knows_trainer_2,',
])

# npc9 Alayen: warrior. L2->7, one-handed 180, riding 5.
data = replace_npc_entry(T, data, "npc9", [
  "  # FewerBandits v5: warrior, L7, one-handed 180, riding 5",
  '  ["npc9","Alayen","Alayen",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_b,itm_tab_shield_heater_cav_a,itm_mail_hauberk,itm_guard_helmet,itm_iron_greaves,itm_gauntlets,itm_warhorse],',
  '   str_13|agi_10|int_8|cha_9|level(7),wpex(180,150,130,90,90,100),knows_ironflesh_4|knows_power_strike_4|knows_riding_5|knows_athletics_4|knows_weapon_master_3|knows_shield_4|knows_leadership_2|knows_tactics_2,',
])

# npc10 Bunduk: warrior / crossbow. L9->14, crossbow 190.
data = replace_npc_entry(T, data, "npc10", [
  "  # FewerBandits v5: warrior/crossbow, L14, crossbow 190",
  '  ["npc10","Bunduk","Bunduk",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_heavy_crossbow,itm_steel_bolts,itm_sword_medieval_b,itm_tab_shield_heater_c,itm_coat_of_plates_red,itm_kettle_hat,itm_plate_boots,itm_gauntlets,itm_hunter],',
  '   str_14|agi_10|int_10|cha_12|level(14),wpex(180,150,130,90,190,110),knows_ironflesh_5|knows_power_strike_4|knows_riding_4|knows_athletics_4|knows_weapon_master_4|knows_shield_3|knows_tactics_2|knows_leadership_2|knows_trainer_3|knows_first_aid_3,',
])

# npc11 Katrin: merchant / warrior. L8->13, one-handed 180, inventory 5.
data = replace_npc_entry(T, data, "npc11", [
  "  # FewerBandits v5: merchant/warrior, L13, one-handed 180, inventory 5",
  '  ["npc11","Katrin","Katrin",tf_female|tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_falchion,itm_tab_shield_kite_c,itm_mail_shirt,itm_kettle_hat,itm_leather_boots,itm_leather_gloves,itm_hunter],',
  '   str_10|agi_13|int_11|cha_11|level(13),wpex(180,140,120,90,90,100),knows_ironflesh_4|knows_power_strike_4|knows_riding_4|knows_athletics_4|knows_weapon_master_3|knows_shield_3|knows_trade_3|knows_first_aid_2|knows_wound_treatment_3|knows_inventory_management_5,',
])

# npc12 Jeremus: medic. L4->9, surgery 5, wound treatment 5, first aid 5.
data = replace_npc_entry(T, data, "npc12", [
  "  # FewerBandits v5: medic, L9, surgery 5, wound treatment 5, first aid 5",
  '  ["npc12","Jeremus","Jeremus",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_a,itm_tab_shield_small_round_b,itm_haubergeon,itm_kettle_hat,itm_leather_boots,itm_leather_gloves,itm_hunter],',
  '   str_10|agi_9|int_15|cha_9|level(9),wpex(150,90,110,90,90,90),knows_ironflesh_3|knows_power_strike_3|knows_riding_4|knows_athletics_3|knows_weapon_master_2|knows_shield_3|knows_surgery_5|knows_wound_treatment_5|knows_first_aid_5,',
])

# npc13 Nizar: warrior / cavalry. L3->8, one-handed 180, riding 5.
data = replace_npc_entry(T, data, "npc13", [
  "  # FewerBandits v5: warrior/cavalry, L8, one-handed 180, riding 5",
  '  ["npc13","Nizar","Nizar",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_scimitar_b,itm_tab_shield_small_round_c,itm_mamluke_mail,itm_sarranid_veiled_helmet,itm_sarranid_boots_d,itm_scale_gauntlets,itm_courser],',
  '   str_10|agi_10|int_13|cha_10|level(8),wpex(180,130,150,90,90,110),knows_ironflesh_3|knows_power_strike_4|knows_riding_5|knows_athletics_4|knows_weapon_master_3|knows_shield_4|knows_leadership_3,',
])

# npc14 Lezalit: warrior / trainer. L5->10, trainer 5, one-handed 190.
data = replace_npc_entry(T, data, "npc14", [
  "  # FewerBandits v5: warrior/trainer, L10, trainer 5, one-handed 190",
  '  ["npc14","Lezalit","Lezalit",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_c,itm_tab_shield_heater_cav_a,itm_heraldic_mail_with_surcoat,itm_bascinet,itm_plate_boots,itm_gauntlets,itm_warhorse],',
  '   str_11|agi_10|int_12|cha_10|level(10),wpex(190,150,140,90,90,100),knows_ironflesh_4|knows_power_strike_4|knows_riding_5|knows_athletics_4|knows_weapon_master_4|knows_shield_4|knows_trainer_5|knows_leadership_3,',
])

# npc15 Artimenner: engineer. L7->12, engineer 6, tactics 3.
data = replace_npc_entry(T, data, "npc15", [
  "  # FewerBandits v5: engineer, L12, engineer 6, tactics 3",
  '  ["npc15","Artimenner","Artimenner",tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_medieval_b,itm_tab_shield_kite_c,itm_mail_hauberk,itm_kettle_hat,itm_iron_greaves,itm_gauntlets,itm_hunter],',
  '   str_11|agi_11|int_14|cha_10|level(12),wpex(170,130,120,110,90,100),knows_ironflesh_3|knows_power_strike_4|knows_riding_4|knows_athletics_4|knows_weapon_master_3|knows_shield_3|knows_engineer_6|knows_tactics_3|knows_trade_4|knows_tracking_2|knows_spotting_2,',
])

# npc16 Klethi: tracker / thrower. L2->7, throwing 190, power throw 5.
data = replace_npc_entry(T, data, "npc16", [
  "  # FewerBandits v5: tracker/thrower, L7, throwing 190, power throw 5",
  '  ["npc16","Klethi","Klethi",tf_female|tf_hero|tf_unmoveable_in_party_window, 0, reserved, fac_commoners,[itm_sword_viking_2_small,itm_heavy_throwing_axes,itm_tab_shield_small_round_b,itm_lamellar_vest,itm_vaegir_fur_helmet,itm_leather_boots,itm_leather_gloves,itm_saddle_horse],',
  '   str_9|agi_14|int_9|cha_9|level(7),wpex(170,110,120,120,90,190),knows_ironflesh_2|knows_power_strike_3|knows_power_throw_5|knows_riding_4|knows_athletics_5|knows_weapon_master_3|knows_tracking_3|knows_pathfinding_2|knows_shield_2,',
])
save(T, data)

# ---------------------------------------------------------------- 2. tavern placement
data = load(S)

anchor = (
  '      (call_script, "script_update_companion_candidates_in_taverns"),' + CRLF
)
placement = (
  anchor +
  '      # FewerBandits v5: gather all 16 companions in two taverns so the' + CRLF +
  '      # player never has to search the map. npc1-8 go to the starting' + CRLF +
  '      # town, npc9-16 to the nearest other town. Native scatters them' + CRLF +
  '      # randomly; the 15-day reshuffle trigger is disabled in' + CRLF +
  '      # module_triggers.py (see the note there), so they stay put.' + CRLF +
  '      (try_begin),' + CRLF +
  '        (is_between, "$g_starting_town", towns_begin, towns_end),' + CRLF +
  '      (else_try),' + CRLF +
  '        (assign, "$g_starting_town", "p_town_6"), # FewerBandits v5: fallback Praven' + CRLF +
  '      (try_end),' + CRLF +
  '      (assign, ":fb_nearest_town", -1),' + CRLF +
  '      (assign, ":fb_nearest_dist", 1000000),' + CRLF +
  '      (try_for_range, ":fb_town", towns_begin, towns_end),' + CRLF +
  '        (neq, ":fb_town", "$g_starting_town"),' + CRLF +
  '        (store_distance_to_party_from_party, ":fb_dist", "$g_starting_town", ":fb_town"),' + CRLF +
  '        (lt, ":fb_dist", ":fb_nearest_dist"),' + CRLF +
  '        (assign, ":fb_nearest_dist", ":fb_dist"),' + CRLF +
  '        (assign, ":fb_nearest_town", ":fb_town"),' + CRLF +
  '      (try_end),' + CRLF +
  '      (try_begin),' + CRLF +
  '        (gt, ":fb_nearest_town", 0),' + CRLF +
  '      (else_try),' + CRLF +
  '        (assign, ":fb_nearest_town", "$g_starting_town"),' + CRLF +
  '      (try_end),' + CRLF +
  '      (try_for_range, ":fb_npc", companions_begin, companions_end),' + CRLF +
  '        (store_sub, ":fb_idx", ":fb_npc", companions_begin),' + CRLF +
  '        (try_begin),' + CRLF +
  '          (lt, ":fb_idx", 8),' + CRLF +
  '          (troop_set_slot, ":fb_npc", slot_troop_cur_center, "$g_starting_town"),' + CRLF +
  '        (else_try),' + CRLF +
  '          (troop_set_slot, ":fb_npc", slot_troop_cur_center, ":fb_nearest_town"),' + CRLF +
  '        (try_end),' + CRLF +
  '      (try_end),' + CRLF +
  '      (str_store_party_name, s1, "$g_starting_town"),' + CRLF +
  '      (str_store_party_name, s2, ":fb_nearest_town"),' + CRLF +
  '      (display_message, "str_fb_companions_gathered"),' + CRLF
)
data = replace(S, data, anchor, placement)
save(S, data)

# ---------------------------------------------------------------- 3. disable 15-day reshuffle
data = load(G)
old_trigger = (
  '   (24 * 15 , 0, 0, ' + CRLF +
  '   [' + CRLF +
  '    (call_script, "script_update_companion_candidates_in_taverns"),' + CRLF +
  '    ],' + CRLF +
  '   []' + CRLF +
  '   ),' + CRLF
)
new_trigger = (
  '   (24 * 15 , 0, 0, ' + CRLF +
  '   [' + CRLF +
  '    # FewerBandits v5: reshuffle disabled -- companions stay in their' + CRLF +
  '    # starting taverns (see game_start). Same treatment vanilla already' + CRLF +
  '    # gave the 72h trigger in module_simple_triggers.py.' + CRLF +
  '    # (call_script, "script_update_companion_candidates_in_taverns"),' + CRLF +
  '    ],' + CRLF +
  '   []' + CRLF +
  '   ),' + CRLF
)
data = replace(G, data, old_trigger, new_trigger)
save(G, data)

# ---------------------------------------------------------------- 4. message string
data = load(N)
# Two cp1254 dash bytes (0x97 em dash, 0x96 en dash) in English flavor text
# must go first: the file is about to become utf-8, and those bytes are not
# valid utf-8. They read as plain "-" afterwards; meaning unchanged.
n97 = data.count(b"\x97")
assert n97 == 1, "module_strings.py: expected 1 x 0x97, found %d" % n97
data = data.replace(b"\x97", b"-")
print("OK module_strings.py: 1 x 0x97 -> '-'")
n96 = data.count(b"\x96")
assert n96 == 1, "module_strings.py: expected 1 x 0x96, found %d" % n96
data = data.replace(b"\x96", b"-")
print("OK module_strings.py: 1 x 0x96 -> '-'")
data = replace(N, data, "# -*- coding: cp1254 -*-", "# -*- coding: utf-8 -*-")
anchor_str = (
  '  ("npc16_1","-Good with throwing and 1h^-Poor with 2h and crossbows"),' + CRLF
)
new_str = (
  anchor_str +
  '  # FewerBandits v5: game-start message naming the two companion taverns' + CRLF +
  '  ("fb_companions_gathered", "åå­ä½åä¼´é½å¨éé¦éç­ä½ ï¼{s1}æå«ä½ï¼{s2}æå«ä½ã"),' + CRLF
)
data = replace(N, data, anchor_str, new_str)
save(N, data)

print("All v5 edits applied.")
