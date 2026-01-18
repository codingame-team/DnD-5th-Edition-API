import os
from pathlib import Path

import random

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Point3, Vec3
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText

class LabyrinthGame(ShowBase):
    def _init_(self):
        ShowBase._init_(self)
        self.disableMouse()  # Disable default camera control

        # Load the labyrinth environment
        self.labyrinth = self.loader.loadModel(f"{models_path}/environment")
        self.labyrinth.reparentTo(self.render)
        self.labyrinth.setScale(0.25, 0.25, 0.25)
        self.labyrinth.setPos(-8, 42, 0)

        # Load the character
        self.character = Actor("f{models_path}/panda-model", {"walk": f"{models_path}/panda-walk4"})
        self.character.reparentTo(self.render)
        self.character.setScale(0.005)
        self.character.setPos(0, 0, 0)

        # Control movement
        self.accept("arrow_up", self.setKey, ["forward", True])
        self.accept("arrow_up-up", self.setKey, ["forward", False])
        self.accept("arrow_down", self.setKey, ["backward", True])
        self.accept("arrow_down-up", self.setKey, ["backward", False])
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_right-up", self.setKey, ["right", False])

        # Key state
        self.keys = {"forward": False, "backward": False, "left": False, "right": False}
        self.speed = 5

        # Add monsters
        self.monsters = []
        for i in range(5):
            monster = self.loader.loadModel(f"{models_path}/panda-model")
            monster.reparentTo(self.render)
            monster.setScale(0.002)
            monster.setPos(random.randint(-20, 20), random.randint(-20, 20), 0)
            self.monsters.append(monster)

        # Add collision detection
        self.taskMgr.add(self.move_task, "moveTask")

    def setKey(self, key, value):
        self.keys[key] = value

    def move_task(self, task):
        dt = globalClock.getDt()
        movement = Vec3(0, 0, 0)

        if self.keys["forward"]:
            movement += Vec3(0, self.speed * dt, 0)
        if self.keys["backward"]:
            movement += Vec3(0, -self.speed * dt, 0)
        if self.keys["left"]:
            self.character.setH(self.character.getH() + 300 * dt)
        if self.keys["right"]:
            self.character.setH(self.character.getH() - 300 * dt)

        self.character.setPos(self.character.getPos() + self.character.getQuat().xform(movement))

        # Check for collisions with monsters
        char_pos = self.character.getPos()
        for monster in self.monsters:
            if (char_pos - monster.getPos()).length() < 1:
                self.monsters.remove(monster)
                monster.removeNode()
                self.show_message("Monster Defeated!")

        return Task.cont

    def show_message(self, message):
        text = OnscreenText(text=message, pos=(0, 0.8), scale=0.07, fg=(1, 0, 0, 1), align=TextNode.ACenter)
        self.taskMgr.doMethodLater(2, lambda task: text.destroy(), 'clearMessageTask')



# Option 1: Using environment variable (recommended)
models_path = os.getenv('PANDA3D_MODELS_PATH', '/Library/Developer/Panda3D/models/')

# Option 2: Using Path for cross-platform compatibility
# models_path = str(Path('/Library/Developer/Panda3D/models/').resolve())

game = LabyrinthGame()
game.run()