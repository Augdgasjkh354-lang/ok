#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FewerBandits v6: three more tavern mercenaries, same standard as v4.
#
# 1. ç ´åéå¼© fb_siege_crossbowman "Siege Crossbowman" / "Siege Crossbowmen"
#    Benchmark: Rhodok Sharpshooter (L25, str14/agi5, crossbow 140,
#    ironflesh3/shield4/power_strike4/athletics6).
#    New: L28, str14/agi7, crossbow 210, ironflesh5/shield6/power_strike5/
#    athletics7, one-handed 130 sidearm. Beats the benchmark on every key stat.
# 2. ç¾é£éªå° fb_gale_horse_archer "Gale Horse Archer" / "Gale Horse Archers"
#    Benchmark: Khergit Veteran Horse Archer (L21, def_attrib 5/5/4/4,
#    archery 130, riding7, horse_archery7, power_draw5, ironflesh3).
#    New: L26, str12/agi8, archery 200, riding8, horse_archery8,
#    power_draw6, ironflesh4. Beats the benchmark on every key stat.
# 3. æ­å²³åå£« fb_mountain_swordsman "Mountain Swordsman" / "Mountain Swordsmen"
#    Benchmark: Nord Huscarl = nord_champion (L28, def_attrib 5/5/4/4,
#    wp(170) i.e. two-handed 170, ironflesh7/power_strike7/athletics7/
#    shield6).
#    New: L30, str12/agi7, two-handed 210, power_strike9, ironflesh8,
#    athletics8. Beats the benchmark on strength, power strike and
#    two-handed proficiency (the three stats the task names).
#
# All three: single tier, no upgrade line, vanilla items only, inserted
# right before "mercenaries_end" so they fall inside the
# mercenary_troops_begin..mercenary_troops_end range used by
# script_update_mercenary_units_of_towns (uniform random pick per town,
# 3-8 men). Pool grows from 10 types (7 vanilla + 3 fb) to 13 types.
# Wages / hiring cost are game-computed from level and stats, not tuned here.
#
# Names follow the v5 lesson from the start: English display names in
# module_troops.py, Chinese via troops.csv (same byte format as the v5 file:
# UTF-8 with BOM, CRLF, one U+0020 between each Chinese character, one
# U+3000 full-width space at the end of the value).
#   trp_fb_siege_crossbowman|ç ´ å é å¼©<U+3000>
#   trp_fb_gale_horse_archer|ç¾ é£ éª å°<U+3000>
#   trp_fb_mountain_swordsman|æ­ å²³ å å£«<U+3000>
# (plus the _pl line for each, same value.)
#
# NOTE: inserting troops before mercenaries_end shifts the numeric index of
# every troop after that point, so old savegames are NOT compatible with v6
# (troop references in saves are by index). A new game is required.
#
# Run from anywhere: python3 apply_fb_v6.py
# Outputs: build/module_troops.py (3 new troops), troops.csv (1340 -> 1346).
# Then rebuild with python2.7 process_*.py as usual.

W = "/home/hatch/workspace/warband-mod/"
B = W + "build/"
CRLF = "\r\n"

def load_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def save_bytes(path, data):
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

# ---- 0. no id conflicts -----------------------------------------------------
troops_py = B + "module_troops.py"
data = load_bytes(troops_py)
for tid in ("fb_siege_crossbowman", "fb_gale_horse_archer", "fb_mountain_swordsman"):
    assert ('"%s"' % tid).encode("utf-8") not in data, "troop id already exists: %s" % tid
print("OK: no id conflicts for the 3 new troops")

# ---- 1. module_troops.py: insert before mercenaries_end --------------------
anchor = (
    '  ["mercenaries_end","mercenaries_end","mercenaries_end",0,no_scene,reserved,fac_commoners,' + CRLF +
    "   []," + CRLF +
    "   def_attrib|level(4),wp(60),knows_common,mercenary_face_1, mercenary_face_2]," + CRLF
)

new_troops = (
  "  # FewerBandits v6: new tavern mercenary - siege crossbowman, beats Rhodok Sharpshooter (L25, crossbow 140)" + CRLF +
  '  ["fb_siege_crossbowman","Siege Crossbowman","Siege Crossbowmen",tf_guarantee_boots|tf_guarantee_armor|tf_guarantee_helmet|tf_guarantee_ranged|tf_guarantee_shield,no_scene,reserved,fac_commoners,' + CRLF +
  "   [itm_sniper_crossbow,itm_steel_bolts,itm_sword_medieval_b,itm_military_pick,itm_tab_shield_pavise_c,itm_plate_armor,itm_coat_of_plates_red,itm_haubergeon,itm_kettle_hat,itm_mail_coif,itm_guard_helmet,itm_great_helmet,itm_bascinet,itm_plate_boots,itm_iron_greaves,itm_gauntlets]," + CRLF +
  "   str_14|agi_7|int_4|cha_4|level(28),wp_one_handed (130) | wp_two_handed (110) | wp_polearm (110) | wp_archery (100) | wp_crossbow (210) | wp_throwing (100),knows_common|knows_ironflesh_5|knows_shield_6|knows_power_strike_5|knows_athletics_7,mercenary_face_1, mercenary_face_2]," + CRLF +
  "  # FewerBandits v6: new tavern mercenary - horse archer, beats Khergit Veteran Horse Archer (L21, archery 130, riding7, horse_archery7)" + CRLF +
  '  ["fb_gale_horse_archer","Gale Horse Archer","Gale Horse Archers",tf_mounted|tf_guarantee_boots|tf_guarantee_armor|tf_guarantee_ranged|tf_guarantee_helmet|tf_guarantee_horse,no_scene,reserved,fac_commoners,' + CRLF +
  "   [itm_war_bow,itm_long_bow,itm_khergit_bow,itm_arrows,itm_barbed_arrows,itm_khergit_arrows,itm_sword_khergit_3,itm_winged_mace,itm_warhorse,itm_charger,itm_hunter,itm_steppe_horse,itm_lamellar_armor,itm_mail_shirt,itm_leather_jerkin,itm_kettle_hat,itm_mail_coif,itm_leather_cap,itm_leather_boots,itm_splinted_leather_greaves]," + CRLF +
  "   str_12|agi_8|int_4|cha_4|level(26),wp_one_handed (130) | wp_two_handed (110) | wp_polearm (110) | wp_archery (200) | wp_crossbow (100) | wp_throwing (130),knows_common|knows_riding_8|knows_horse_archery_8|knows_power_draw_6|knows_ironflesh_4|knows_power_throw_3,mercenary_face_1, mercenary_face_2]," + CRLF +
  "  # FewerBandits v6: new tavern mercenary - two-handed swordsman, beats Nord Huscarl (L28, two-handed 170, power_strike7)" + CRLF +
  '  ["fb_mountain_swordsman","Mountain Swordsman","Mountain Swordsmen",tf_mounted|tf_guarantee_boots|tf_guarantee_armor|tf_guarantee_helmet|tf_guarantee_shield,no_scene,reserved,fac_commoners,' + CRLF +
  "   [itm_sword_two_handed_b,itm_sword_two_handed_a,itm_bastard_sword_b,itm_sword_medieval_c,itm_great_axe,itm_tab_shield_heater_cav_a,itm_coat_of_plates_red,itm_plate_armor,itm_haubergeon,itm_mail_chausses,itm_iron_greaves,itm_plate_boots,itm_guard_helmet,itm_great_helmet,itm_bascinet,itm_full_helm,itm_gauntlets,itm_leather_gloves]," + CRLF +
  "   str_12|agi_7|int_4|cha_4|level(30),wp_one_handed (150) | wp_two_handed (210) | wp_polearm (130) | wp_archery (100) | wp_crossbow (100) | wp_throwing (120),knows_common|knows_ironflesh_8|knows_power_strike_9|knows_athletics_8|knows_shield_3,mercenary_face_1, mercenary_face_2]," + CRLF
)
data = replace(troops_py, data, anchor, new_troops + anchor, 1)
save_bytes(troops_py, data)
print("OK module_troops.py: 3 new mercenaries inserted before mercenaries_end")

# ---- 2. troops.csv: v5 file (1340 lines) + 6 lines -------------------------
csv_path = W + "troops.csv"
csv_data = load_bytes(csv_path)
assert csv_data[:3] == b"\xef\xbb\xbf", "troops.csv lost its UTF-8 BOM"
assert csv_data.endswith(b"\r\n"), "troops.csv does not end with CRLF"
assert csv_data.count(b"\n") == csv_data.count(b"\r\n") == 1340, \
    "troops.csv: expected 1340 lines, got %d" % csv_data.count(b"\n")
assert csv_data.endswith("trp_fb_falcon_archer_pl|ç é¹° ç¥ å°\u3000\r\n".encode("utf-8")), \
    "troops.csv does not end with the v5 falcon archer line"

new_lines = [
    u"trp_fb_siege_crossbowman|ç ´ å é å¼©\u3000",
    u"trp_fb_siege_crossbowman_pl|ç ´ å é å¼©\u3000",
    u"trp_fb_gale_horse_archer|ç¾ é£ éª å°\u3000",
    u"trp_fb_gale_horse_archer_pl|ç¾ é£ éª å°\u3000",
    u"trp_fb_mountain_swordsman|æ­ å²³ å å£«\u3000",
    u"trp_fb_mountain_swordsman_pl|æ­ å²³ å å£«\u3000",
]
for ln in new_lines:
    key = ln.split(u"|")[0]
    assert (key + u"|").encode("utf-8") not in csv_data, "key already in troops.csv: %s" % key
appended = "".join(ln + u"\r\n" for ln in new_lines).encode("utf-8")
out = csv_data + appended
save_bytes(csv_path, out)

check = load_bytes(csv_path)
assert check[:len(csv_data)] == csv_data, "first 1340 lines differ from v5 file"
assert check[len(csv_data):] == appended, "appended block mismatch"
assert check.count(b"\n") == check.count(b"\r\n") == 1346, "expected 1346 lines"
assert check[:3] == b"\xef\xbb\xbf" and check.endswith(b"\r\n")
for ln in new_lines:
    assert check.count(ln.encode("utf-8")) == 1, "line not present exactly once: %s" % ln
print("OK troops.csv: 1346 lines (1340 v5 + 6 new), BOM + CRLF + U+3000 intact")
print("DONE")
