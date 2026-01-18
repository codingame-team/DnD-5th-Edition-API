-- T_Monsters definition

CREATE TABLE T_Monsters (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	"name" TEXT(30),
	armor_class INTEGER,
	hit_points INTEGER,
	hit_dice TEXT(3),
	xp INTEGER,
	challenge_rating INTEGER,
	CONSTRAINT T_Monsters_PK PRIMARY KEY (id)
);

-- T_Proficiencies definition

CREATE TABLE T_Proficiencies (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	"index" TEXT(20),
	"name" TEXT(20),
	"type" TEXT(15),
	CONSTRAINT T_Proficiencies_PK PRIMARY KEY (id)
);

-- T_CharacterProfs definition

CREATE TABLE T_CharacterProfs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	idCharacter INTEGER,
	idProf INTEGER,
	CONSTRAINT T_CharacterProfs_PK PRIMARY KEY (id),
	CONSTRAINT T_CharacterProfs_FK FOREIGN KEY (idCharacter) REFERENCES T_Characters(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT T_CharacterProfs_FK_1 FOREIGN KEY (idProf) REFERENCES T_Proficiencies(id) ON DELETE CASCADE ON UPDATE CASCADE
);