from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GameConfig:
    map_width: int
    map_height: int
    term_width: int
    term_height: int

    def get_view_dimensions(self) -> Tuple[int, int]:
        """Calculate view dimensions based on terminal size."""
        view_width = min(self.term_width // 2, self.map_width)
        view_height = min(self.term_height - 2, self.map_height)
        return view_width, view_height


class GameRenderer:
    def __init__(self, stdscr, game_map, camera):
        self.stdscr = stdscr
        self.game_map = game_map
        self.camera = camera

    def render_frame(self, player, enemies):
        """Render a complete frame of the game."""
        self.camera.follow(player)
        self.stdscr.clear()
        self._draw_map(player, enemies)
        self._draw_status_bar(player)
        self.stdscr.refresh()

    def _draw_map(self, player, enemies):
        """Draw the game map with all entities."""
        draw_map(self.stdscr, self.game_map, player, enemies, self.camera)

    def _draw_status_bar(self, player):
        """Draw the status bar below the map."""
        status = self._format_status(player)
        self.stdscr.addstr(self.camera.view_height, 0, status)

    @staticmethod
    def _format_status(player) -> str:
        """Format the status bar text."""
        return f"HP: {player.hp} | Pos: ({player.x},{player.y})"


class GameState:
    def __init__(self, config: GameConfig):
        self.config = config
        self.player = self._initialize_player()
        self.enemies = self._initialize_enemies()

    def _initialize_player(self) -> "Player":
        """Initialize the player in the center of the map."""
        return Player(
            name="Héros", x=self.config.map_width // 2, y=self.config.map_height // 2
        )

    def _initialize_enemies(self) -> List["Enemy"]:
        """Initialize enemies on the map."""
        return initialize_enemies(5, self.game_map)


class GameLoop:
    def __init__(self, stdscr, config: GameConfig):
        self.stdscr = stdscr
        self.config = config
        view_width, view_height = config.get_view_dimensions()

        self.camera = Camera(
            map_width=config.map_width,
            map_height=config.map_height,
            view_width=view_width,
            view_height=view_height,
        )

        self.game_state = GameState(config)
        self.renderer = GameRenderer(stdscr, game_map, self.camera)

    def run(self):
        """Main game loop."""
        while True:
            self.renderer.render_frame(self.game_state.player, self.game_state.enemies)
            if not self._handle_input():
                break

    def _handle_input(self) -> bool:
        """Handle user input. Returns False if game should exit."""
        key = self.stdscr.getch()

        if key == KEY_RESIZE:
            self._handle_resize()
        # Add other input handling here

        return True

    def _handle_resize(self):
        """Handle terminal resize event."""
        term_height, term_width = self.stdscr.getmaxyx()
        self.config.term_height = term_height
        self.config.term_width = term_width

        view_width, view_height = self.config.get_view_dimensions()
        self.camera.view_width = view_width
        self.camera.view_height = view_height


def main(stdscr):
    config = GameConfig(
        map_width=map_width,
        map_height=map_height,
        term_width=term_width,
        term_height=term_height,
    )

    game = GameLoop(stdscr, config)
    game.run()

if __name__ == "__main__":
    from curses import wrapper
    wrapper(main)

