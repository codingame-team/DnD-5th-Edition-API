import DungeonGenerator as dg5

barbarian = dg5.Barbarian
aset = dg5.AdventureSet.summary
dungeon = dg5.Dungeon(cr=1)
room = dungeon.rooms
print(dg5.Fighter.weapon_options.flat)
#print(room)
monster = dg5.MonsterGroup.cr_mod(6, 10, 'Insane')
print(dungeon.dungeon_levels)
dungeon = dg5.dungeon_npc(3, 3)

# dungeon = dungeon_generator.Generator(config={'col_size': 10, 'row_size': 10, 'room_number': 5})
pass
