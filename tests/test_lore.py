import unittest

from lotr_adventure.domain.lore import LoreCatalog


class LoreTests(unittest.TestCase):
    def test_loads_locations_and_npcs(self):
        lore = LoreCatalog.load()
        self.assertIsNotNone(lore.get_location("Bag End"))
        self.assertIsNotNone(lore.get_npc("Gandalf"))

    def test_find_location_from_linked_route(self):
        lore = LoreCatalog.load()
        location = lore.find_location("pony", from_location="Bree")
        self.assertIsNotNone(location)
        self.assertEqual(location.name, "The Prancing Pony")

    def test_find_location_does_not_match_unlinked_global_place_when_route_is_specific(self):
        lore = LoreCatalog.load()
        location = lore.find_location("lake", from_location="The Shire")
        self.assertIsNone(location)

    def test_story_paths_load(self):
        lore = LoreCatalog.load()
        paths = lore.list_story_paths_for_character("frodo")
        self.assertTrue(paths)
        self.assertEqual(paths[0].steps[0].anchor_id, "frodo_departs_shire")

    def test_loads_expanded_hobbit_anchor_and_npc(self):
        lore = LoreCatalog.load()
        anchor = lore.get_anchor("bilbo_at_hidden_door")
        self.assertEqual(anchor.location, "The Hidden Door")
        self.assertIn("Balin", anchor.starting_npcs)
        self.assertTrue(anchor.scene_beats)
        location = lore.get_location("The Hidden Door")
        self.assertIsNotNone(location)
        self.assertIn("Balin", location.resident_npcs)

    def test_loads_new_gandalf_and_bilbo_expansion_anchors(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("gandalf_at_bag_end").location, "Bag End")
        self.assertEqual(lore.get_anchor("gandalf_in_meduseld").location, "Meduseld")
        self.assertEqual(lore.get_anchor("bilbo_in_smaugs_lair").location, "Smaug's Lair")
        self.assertIsNotNone(lore.get_npc("Smaug"))

    def test_loads_new_frodo_and_bilbo_midjourney_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("frodo_at_west_gate").location, "Hollin")
        self.assertEqual(lore.get_anchor("frodo_in_lorien").location, "Lothlórien")
        self.assertEqual(lore.get_anchor("bilbo_in_mirkwood").location, "Mirkwood")
        self.assertIsNotNone(lore.get_npc("Boromir"))
        self.assertIsNotNone(lore.get_npc("Galadriel"))
        self.assertIsNotNone(lore.get_npc("Haldir"))

    def test_loads_sam_gorgoroth_expansion(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("sam_on_gorgoroth").location, "Gorgoroth")
        self.assertIsNotNone(lore.get_location("The Ash Road"))

    def test_loads_frodo_late_fellowship_and_marsh_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("frodo_at_amon_hen").location, "Amon Hen")
        self.assertEqual(lore.get_anchor("frodo_in_dead_marshes").location, "The Dead Marshes")
        self.assertIsNotNone(lore.get_location("The Seat of Seeing"))
        self.assertIsNotNone(lore.get_location("The Dead Faces Mere"))

    def test_loads_balancing_expansions_for_other_paths(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_in_lake_town").location, "Lake-town")
        self.assertEqual(lore.get_anchor("frodo_on_morgul_stairs").location, "The Morgul Stairs")
        self.assertEqual(lore.get_anchor("aragorn_at_black_gate").location, "The Black Gate")
        self.assertEqual(lore.get_anchor("gandalf_on_pelennor").location, "The Pelennor")
        self.assertIsNotNone(lore.get_npc("Bard"))

    def test_loads_endgame_and_healing_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_in_besiegers_camp").location, "The Besiegers' Camp")
        self.assertEqual(lore.get_anchor("bilbo_after_battle").location, "Ravenhill")
        self.assertEqual(lore.get_anchor("frodo_in_shelobs_lair").location, "Shelob's Lair")
        self.assertEqual(lore.get_anchor("frodo_at_sammath_naur").location, "Sammath Naur")
        self.assertEqual(lore.get_anchor("aragorn_in_houses_of_healing").location, "The Houses of Healing")
        self.assertEqual(lore.get_anchor("gandalf_at_black_gate").location, "The Black Gate")
        self.assertIsNotNone(lore.get_location("The Command Tent"))
        self.assertIsNotNone(lore.get_location("The Fire-chamber"))
        self.assertIsNotNone(lore.get_npc("Shelob"))
        self.assertIsNotNone(lore.get_npc("Éowyn"))

    def test_loads_homecoming_and_coronation_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_back_at_bag_end").location, "Bag End")
        self.assertEqual(lore.get_anchor("frodo_at_cormallen").location, "The Field of Cormallen")
        self.assertEqual(lore.get_anchor("frodo_at_grey_havens").location, "The Grey Havens")
        self.assertEqual(lore.get_anchor("sam_back_in_the_shire").location, "Bag End")
        self.assertEqual(lore.get_anchor("aragorn_at_coronation").location, "The Court of the Fountain")
        self.assertEqual(lore.get_anchor("gandalf_at_coronation").location, "The Court of the Fountain")
        self.assertIsNotNone(lore.get_location("The White Ship"))
        self.assertIsNotNone(lore.get_location("The King's Pavilion"))
        self.assertIsNotNone(lore.get_npc("Arwen"))
        self.assertIsNotNone(lore.get_npc("Rosie Cotton"))
        self.assertIsNotNone(lore.get_npc("Círdan"))

    def test_loads_bombadil_beorn_and_woodland_realm_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_at_beorns_house").location, "Beorn's House")
        self.assertEqual(lore.get_anchor("bilbo_in_woodland_realm").location, "The Woodland Realm")
        self.assertEqual(lore.get_anchor("frodo_in_old_forest").location, "The Old Forest")
        self.assertEqual(lore.get_anchor("frodo_at_bombadils_house").location, "Tom Bombadil's House")
        self.assertEqual(lore.get_anchor("frodo_on_barrow_downs").location, "The Barrow-downs")
        self.assertIsNotNone(lore.get_location("The Bee Pastures"))
        self.assertIsNotNone(lore.get_location("The Rain-washed Room"))
        self.assertIsNotNone(lore.get_location("The Wine Cellars"))
        self.assertIsNotNone(lore.get_npc("Beorn"))
        self.assertIsNotNone(lore.get_npc("Tom Bombadil"))
        self.assertIsNotNone(lore.get_npc("Goldberry"))
        self.assertIsNotNone(lore.get_npc("Thranduil"))

    def test_loads_orthanc_dunharrow_and_denethor_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("aragorn_at_dunharrow").location, "Dunharrow")
        self.assertEqual(lore.get_anchor("gandalf_at_orthanc").location, "Isengard")
        self.assertEqual(lore.get_anchor("gandalf_with_denethor").location, "The Citadel")
        self.assertIsNotNone(lore.get_location("The Dimholt Door"))
        self.assertIsNotNone(lore.get_location("The Orthanc Steps"))
        self.assertIsNotNone(lore.get_location("The Steward's Hall"))
        self.assertIsNotNone(lore.get_npc("Saruman"))
        self.assertIsNotNone(lore.get_npc("Gríma Wormtongue"))
        self.assertIsNotNone(lore.get_npc("Denethor"))

    def test_loads_scouring_of_the_shire_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("frodo_in_scouring").location, "Bywater")
        self.assertEqual(lore.get_anchor("sam_in_scouring").location, "Bywater")
        self.assertIsNotNone(lore.get_location("The Party Field"))
        self.assertIsNotNone(lore.get_location("The Bywater Road"))
        self.assertIsNotNone(lore.get_npc("Farmer Cotton"))
        self.assertIsNotNone(lore.get_npc("Lobelia Sackville-Baggins"))

    def test_loads_pelargir_rath_dinen_and_gondor_cast_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("aragorn_at_pelargir").location, "Pelargir")
        self.assertEqual(lore.get_anchor("gandalf_in_rath_dinen").location, "Rath Dínen")
        self.assertIsNotNone(lore.get_location("The Quays of Pelargir"))
        self.assertIsNotNone(lore.get_location("The Captured Corsair Ships"))
        self.assertIsNotNone(lore.get_location("The Silent Street"))
        self.assertIsNotNone(lore.get_npc("Halbarad"))
        self.assertIsNotNone(lore.get_npc("Elladan"))
        self.assertIsNotNone(lore.get_npc("Elrohir"))
        self.assertIsNotNone(lore.get_npc("Beregond"))
        self.assertIsNotNone(lore.get_npc("Ioreth"))
        self.assertIsNotNone(lore.get_npc("Prince Imrahil"))

    def test_loads_bilbo_eagles_and_front_gate_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_with_eagles").location, "The Eagles' Eyrie")
        self.assertEqual(lore.get_anchor("bilbo_at_front_gate").location, "The Front Gate")
        self.assertIsNotNone(lore.get_location("The Eagle Ledge"))
        self.assertIsNotNone(lore.get_location("The Carrock"))
        self.assertIsNotNone(lore.get_npc("Great Eagle"))

    def test_loads_frodo_emyn_muil_and_henneth_annun_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("frodo_in_emyn_muil").location, "Emyn Muil")
        self.assertEqual(lore.get_anchor("frodo_at_henneth_annun").location, "Henneth Annûn")
        self.assertIsNotNone(lore.get_location("The Slinker Stair"))
        self.assertIsNotNone(lore.get_location("The Forbidden Pool"))
        self.assertIsNotNone(lore.get_location("The Window on the West"))

    def test_loads_sam_henneth_annun_expansion(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("sam_in_shire").location, "The Shire")
        self.assertEqual(lore.get_anchor("sam_at_henneth_annun").location, "Henneth Annûn")
        self.assertEqual(lore.story_paths["sam_faithful_heart"].steps[0].anchor_id, "sam_in_shire")
        self.assertEqual(lore.story_paths["sam_faithful_heart"].steps[5].anchor_id, "sam_at_henneth_annun")

    def test_loads_aragorn_fangorn_and_gandalf_moria_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("aragorn_at_weathertop").location, "Weathertop")
        self.assertEqual(lore.story_paths["aragorn_returning_king"].steps[1].anchor_id, "aragorn_at_weathertop")
        self.assertEqual(lore.get_anchor("aragorn_in_fangorn").location, "Fangorn Forest")
        self.assertEqual(lore.get_anchor("gandalf_in_moria").location, "The Bridge of Khazad-dum")
        self.assertIsNotNone(lore.get_location("The Chamber of Mazarbul"))
        self.assertIsNotNone(lore.get_location("The Dimrill Stair"))
        self.assertIsNotNone(lore.get_npc("Durin's Bane"))

    def test_loads_last_debate_and_great_gate_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("aragorn_at_last_debate").location, "The Citadel")
        self.assertEqual(lore.get_anchor("gandalf_at_great_gate").location, "The Great Gate")
        self.assertIsNotNone(lore.get_location("The Great Gate"))
        self.assertIsNotNone(lore.get_npc("The Witch-king of Angmar"))

    def test_loads_bilbo_early_journey_expansions(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_anchor("bilbo_with_trolls").location, "Trollshaws")
        self.assertEqual(lore.get_anchor("bilbo_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.get_anchor("bilbo_in_goblin_town").location, "Goblin Town")
        self.assertIsNotNone(lore.get_location("The Trolls' Clearing"))
        self.assertIsNotNone(lore.get_location("The Great Goblin's Hall"))
        self.assertIsNotNone(lore.get_npc("William Huggins"))
        self.assertIsNotNone(lore.get_npc("The Great Goblin"))

    def test_loads_late_hobbit_supporting_cast(self):
        lore = LoreCatalog.load()
        self.assertIsNotNone(lore.get_npc("Dain Ironfoot"))
        self.assertIsNotNone(lore.get_npc("The Master of Lake-town"))
        self.assertIsNotNone(lore.get_npc("Dwalin"))
        self.assertIsNotNone(lore.get_npc("Bofur"))
        self.assertIn("The Master of Lake-town", lore.get_anchor("bilbo_in_lake_town").starting_npcs)
        self.assertIn("Bofur", lore.get_anchor("thorin_in_lake_town").starting_npcs)
        self.assertIn("Dwalin", lore.get_anchor("thorin_at_front_gate").starting_npcs)
        self.assertIn("Dain Ironfoot", lore.get_anchor("bard_in_besiegers_camp").starting_npcs)
        self.assertIn("Dain Ironfoot", lore.get_anchor("bilbo_after_battle").starting_npcs)

    def test_loads_rohan_supporting_cast(self):
        lore = LoreCatalog.load()
        self.assertIsNotNone(lore.get_npc("Erkenbrand"))
        self.assertIsNotNone(lore.get_npc("Elfhelm"))
        self.assertIn("Erkenbrand", lore.get_anchor("theoden_at_helms_deep").starting_npcs)
        self.assertIn("Elfhelm", lore.get_anchor("eomer_at_dunharrow").starting_npcs)
        self.assertIn("Halbarad", lore.get_anchor("aragorn_at_dunharrow").starting_npcs)

    def test_loads_gondor_supporting_cast(self):
        lore = LoreCatalog.load()
        self.assertIsNotNone(lore.get_npc("Bergil"))
        self.assertIsNotNone(lore.get_npc("Hurin of the Keys"))
        self.assertIn("Bergil", lore.get_anchor("pippin_in_minas_tirith").starting_npcs)
        self.assertIn("Hurin of the Keys", lore.get_anchor("pippin_with_denethor").starting_npcs)
        self.assertIn("Hurin of the Keys", lore.get_anchor("aragorn_at_coronation").starting_npcs)

    def test_loads_pippin_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("pippin").name, "Peregrin Took")
        self.assertEqual(lore.get_anchor("pippin_in_shire").location, "The Shire")
        self.assertEqual(lore.story_paths["pippin_in_gondor"].steps[0].anchor_id, "pippin_in_shire")
        self.assertIn("pippin_with_denethor", [step.anchor_id for step in lore.story_paths["pippin_in_gondor"].steps])
        self.assertEqual(lore.story_paths["pippin_in_gondor"].steps[-1].anchor_id, "pippin_at_coronation")

    def test_loads_merry_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("merry").name, "Meriadoc Brandybuck")
        self.assertEqual(lore.get_anchor("merry_in_shire").location, "The Shire")
        self.assertEqual(lore.story_paths["merry_in_rohan_and_gondor"].steps[0].anchor_id, "merry_in_shire")
        self.assertIn("merry_at_dunharrow", [step.anchor_id for step in lore.story_paths["merry_in_rohan_and_gondor"].steps])
        self.assertEqual(lore.story_paths["merry_in_rohan_and_gondor"].steps[-1].anchor_id, "merry_in_scouring")

    def test_loads_eowyn_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("eowyn").name, "Éowyn")
        self.assertEqual(lore.get_anchor("eowyn_in_meduseld").location, "Meduseld")
        self.assertEqual(lore.story_paths["eowyn_shieldmaiden"].steps[0].anchor_id, "eowyn_in_meduseld")
        self.assertIn("eowyn_in_healing_garden", [step.anchor_id for step in lore.story_paths["eowyn_shieldmaiden"].steps])
        self.assertEqual(lore.story_paths["eowyn_shieldmaiden"].steps[-1].anchor_id, "eowyn_at_coronation")

    def test_loads_faramir_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("faramir").name, "Faramir")
        self.assertEqual(lore.get_anchor("faramir_in_henneth_annun").location, "Henneth Annûn")
        self.assertEqual(lore.story_paths["faramir_captain_and_steward"].steps[0].anchor_id, "faramir_in_henneth_annun")
        self.assertIn("faramir_in_houses_of_healing", [step.anchor_id for step in lore.story_paths["faramir_captain_and_steward"].steps])
        self.assertEqual(lore.story_paths["faramir_captain_and_steward"].steps[-1].anchor_id, "faramir_at_coronation")

    def test_loads_theoden_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("theoden").name, "Théoden")
        self.assertEqual(lore.get_anchor("theoden_in_meduseld").location, "Meduseld")
        self.assertEqual(lore.story_paths["theoden_king_of_rohan"].steps[0].anchor_id, "theoden_in_meduseld")
        self.assertEqual(lore.story_paths["theoden_king_of_rohan"].steps[-1].anchor_id, "theoden_on_pelennor")

    def test_loads_thorin_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("thorin").name, "Thorin Oakenshield")
        self.assertEqual(lore.get_anchor("thorin_in_lake_town").location, "Lake-town")
        self.assertEqual(lore.story_paths["thorin_erebor_restored"].steps[0].anchor_id, "thorin_in_lake_town")
        self.assertEqual(lore.story_paths["thorin_erebor_restored"].steps[-1].anchor_id, "thorin_after_battle")

    def test_loads_bard_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("bard").name, "Bard")
        self.assertEqual(lore.get_anchor("bard_in_lake_town").location, "Lake-town")
        self.assertEqual(lore.story_paths["bard_heir_of_girion"].steps[0].anchor_id, "bard_in_lake_town")
        self.assertIn("bard_against_smaug", [step.anchor_id for step in lore.story_paths["bard_heir_of_girion"].steps])
        self.assertEqual(lore.story_paths["bard_heir_of_girion"].steps[-1].anchor_id, "bard_after_battle")

    def test_loads_eomer_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("eomer").name, "Éomer")
        self.assertEqual(lore.get_anchor("eomer_in_meduseld").location, "Meduseld")
        self.assertEqual(lore.story_paths["eomer_rider_and_king"].steps[0].anchor_id, "eomer_in_meduseld")
        self.assertIn("eomer_at_dunharrow", [step.anchor_id for step in lore.story_paths["eomer_rider_and_king"].steps])
        self.assertEqual(lore.story_paths["eomer_rider_and_king"].steps[-1].anchor_id, "eomer_at_cormallen")

    def test_loads_gimli_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("gimli").name, "Gimli")
        self.assertEqual(lore.get_anchor("gimli_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.story_paths["gimli_axe_and_friendship"].steps[0].anchor_id, "gimli_in_rivendell")
        self.assertIn("gimli_in_fangorn", [step.anchor_id for step in lore.story_paths["gimli_axe_and_friendship"].steps])
        self.assertIn("gimli_in_isengard", [step.anchor_id for step in lore.story_paths["gimli_axe_and_friendship"].steps])
        self.assertEqual(lore.story_paths["gimli_axe_and_friendship"].steps[-1].anchor_id, "gimli_at_cormallen")

    def test_loads_legolas_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("legolas").name, "Legolas")
        self.assertEqual(lore.get_anchor("legolas_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.story_paths["legolas_memory_and_fellowship"].steps[0].anchor_id, "legolas_in_rivendell")
        self.assertIn("legolas_in_fangorn", [step.anchor_id for step in lore.story_paths["legolas_memory_and_fellowship"].steps])
        self.assertIn("legolas_in_isengard", [step.anchor_id for step in lore.story_paths["legolas_memory_and_fellowship"].steps])
        self.assertEqual(lore.story_paths["legolas_memory_and_fellowship"].steps[-1].anchor_id, "legolas_at_cormallen")

    def test_loads_boromir_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("boromir").name, "Boromir")
        self.assertEqual(lore.get_anchor("boromir_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.story_paths["boromir_gondors_burden"].steps[0].anchor_id, "boromir_in_rivendell")
        self.assertEqual(lore.story_paths["boromir_gondors_burden"].steps[-1].anchor_id, "boromir_at_amon_hen")

    def test_loads_treebeard_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("treebeard").name, "Treebeard")
        self.assertEqual(lore.get_anchor("treebeard_in_fangorn").location, "Fangorn Forest")
        self.assertEqual(lore.story_paths["treebeard_fangorn_awakened"].steps[0].anchor_id, "treebeard_in_fangorn")
        self.assertEqual(lore.story_paths["treebeard_fangorn_awakened"].steps[-1].anchor_id, "treebeard_at_orthanc")

    def test_loads_galadriel_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("galadriel").name, "Galadriel")
        self.assertEqual(lore.get_anchor("galadriel_in_lorien").location, "Lothlórien")
        self.assertEqual(lore.story_paths["galadriel_keeper_of_the_golden_wood"].steps[0].anchor_id, "galadriel_in_lorien")
        self.assertEqual(lore.story_paths["galadriel_keeper_of_the_golden_wood"].steps[-1].anchor_id, "galadriel_at_grey_havens")

    def test_loads_elrond_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("elrond").name, "Elrond")
        self.assertEqual(lore.get_anchor("elrond_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.story_paths["elrond_memory_and_departure"].steps[0].anchor_id, "elrond_in_rivendell")
        self.assertEqual(lore.story_paths["elrond_memory_and_departure"].steps[-1].anchor_id, "elrond_at_grey_havens")

    def test_loads_gollum_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("gollum").name, "Gollum")
        self.assertEqual(lore.get_anchor("gollum_in_emyn_muil").location, "Emyn Muil")
        self.assertEqual(lore.story_paths["gollum_precious_and_ruin"].steps[0].anchor_id, "gollum_in_emyn_muil")
        self.assertEqual(lore.story_paths["gollum_precious_and_ruin"].steps[-1].anchor_id, "gollum_at_sammath_naur")

    def test_loads_denethor_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("denethor").name, "Denethor")
        self.assertEqual(lore.get_anchor("denethor_in_stewards_hall").location, "The Steward's Hall")
        self.assertEqual(lore.story_paths["denethor_pride_and_pyre"].steps[0].anchor_id, "denethor_in_stewards_hall")
        self.assertEqual(lore.story_paths["denethor_pride_and_pyre"].steps[-1].anchor_id, "denethor_in_rath_dinen")

    def test_loads_saruman_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("saruman").name, "Saruman")
        self.assertEqual(lore.get_anchor("saruman_in_isengard").location, "Isengard")
        self.assertEqual(lore.story_paths["saruman_fall_of_the_voice"].steps[0].anchor_id, "saruman_in_isengard")
        self.assertEqual(lore.story_paths["saruman_fall_of_the_voice"].steps[-1].anchor_id, "saruman_at_bag_end")

    def test_loads_arwen_playable_path(self):
        lore = LoreCatalog.load()
        self.assertEqual(lore.get_character("arwen").name, "Arwen")
        self.assertEqual(lore.get_anchor("arwen_in_rivendell").location, "Rivendell")
        self.assertEqual(lore.story_paths["arwen_evenstar_and_choice"].steps[0].anchor_id, "arwen_in_rivendell")
        self.assertEqual(lore.story_paths["arwen_evenstar_and_choice"].steps[-1].anchor_id, "arwen_at_coronation")

    def test_lore_references_resolve(self):
        lore = LoreCatalog.load()
        for anchor in lore.list_anchors():
            self.assertIsNotNone(lore.get_location(anchor.location), anchor.id)
            for npc_name in anchor.starting_npcs:
                self.assertIsNotNone(lore.get_npc(npc_name), f"{anchor.id}:{npc_name}")
            for exit_name in anchor.available_exits:
                self.assertIsNotNone(lore.get_location(exit_name), f"{anchor.id}:{exit_name}")
        for location in lore.locations.values():
            for linked_name in location.linked_locations:
                linked = lore.get_location(linked_name)
                self.assertIsNotNone(linked, f"{location.name}:{linked_name}")
                self.assertIn(location.name, linked.linked_locations, f"{location.name}:{linked_name}")
            for npc_name in location.resident_npcs:
                self.assertIsNotNone(lore.get_npc(npc_name), f"{location.name}:{npc_name}")
        for path in lore.story_paths.values():
            self.assertIsNotNone(lore.get_character(path.character_id), path.id)
            for step in path.steps:
                anchor = lore.get_anchor(step.anchor_id)
                self.assertIsNotNone(anchor, f"{path.id}:{step.anchor_id}")
                self.assertEqual(anchor.viewpoint_character_id, path.character_id, f"{path.id}:{step.anchor_id}")
                for location_name in step.required_locations:
                    self.assertIsNotNone(lore.get_location(location_name), f"{path.id}:{location_name}")
                for npc_name in step.required_npcs:
                    self.assertIsNotNone(lore.get_npc(npc_name), f"{path.id}:{npc_name}")
