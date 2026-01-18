    Traceback (most recent call last):
      File "/Users/display/PycharmProjects/DnD-5th-Edition-API/pyQTApp/EdgeOfTown/Combat_module.py", line 241, in combat
        best_slot_level: int = attacker.get_best_slot_level(heal_spell=action.spell, target=char)
                               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/display/PycharmProjects/DnD-5th-Edition-API/dao_classes.py", line 1270, in get_best_slot_level
        max_slot_level = max(i for i, slot in enumerate(self.sc.spell_slots) if slot)
    ValueError: max() iterable argument is empty