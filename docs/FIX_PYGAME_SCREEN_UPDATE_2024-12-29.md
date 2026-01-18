# Fix: Pygame screen not updating when character moves

**Date**: December 29, 2024  
**File**: `dungeon_pygame.py`  
**Function**: `move_char()`  
**Status**: ✅ FIXED

## Problem

When the player character moved in the dungeon pygame game, the screen did not update to show the new position. The character appeared to stay in place even though the game logic registered the movement.

## Root Cause

The `Game` class maintains **two sets of position coordinates**:

1. **`game.x, game.y`** - Game-level position tracking
2. **`game.hero.x, game.hero.y`** - Character entity position (GameCharacter wrapper)

### The Issue

In the `move_char()` function, only `game.x` and `game.y` were being updated:

```python
# ❌ BEFORE - Only updates game position
def move_char(game: Game, char: Monster | Character, pos: tuple):
    # ...
    if mh_dist(game.pos, pos) <= 1:
        game.x, game.y = pos  # ❌ Only game.x/y updated
        # game.hero.x/y NOT updated!
    # ...
    else:
        if path:
            if isinstance(char, Character):
                game.x, game.y = path[1]  # ❌ Only game.x/y updated
                # game.hero.x/y NOT updated!
```

### Why This Caused the Problem

The rendering function `update_display()` draws the hero sprite at position `game.hero.x, game.hero.y`:

```python
# In update_display()
def update_display(game, token_images, screen):
    # ...
    # III-2 Afficher les personnages
    image: Surface = sprites[game.id]
    game.hero.draw(screen, image, TILE_SIZE, *view_port_tuple)
    # ^ Uses game.hero.x and game.hero.y internally
```

Since `game.hero.x/y` were never updated, the hero sprite stayed at the initial position, even though `game.x/y` moved.

## Solution

Synchronize `game.hero.x/y` with `game.x/y` whenever the character moves:

```python
# ✅ AFTER - Synchronizes both positions
def move_char(game: Game, char: Monster | Character, pos: tuple):
    # ...
    if mh_dist(game.pos, pos) <= 1:
        game.x, game.y = pos
        # ✅ Synchronize hero position with game position
        if isinstance(char, Character):
            game.hero.old_x, game.hero.old_y = game.hero.x, game.hero.y
            game.hero.x, game.hero.y = game.x, game.y
    # ...
    else:
        if path:
            if isinstance(char, Character):
                game.x, game.y = path[1]
                # ✅ Synchronize hero position with game position
                game.hero.old_x, game.hero.old_y = game.hero.x, game.hero.y
                game.hero.x, game.hero.y = game.x, game.y
```

## Changes Made

### Location 1: Short-distance move (≤1 tile)
```python
if mh_dist(game.pos, pos) <= 1:
    game.x, game.y = pos
    # ✅ ADD: Synchronize hero position
    if isinstance(char, Character):
        game.hero.old_x, game.hero.old_y = game.hero.x, game.hero.y
        game.hero.x, game.hero.y = game.x, game.y
```

### Location 2: Path-finding move (>1 tile)
```python
if isinstance(char, Character):
    game.x, game.y = path[1]
    # ✅ ADD: Synchronize hero position
    game.hero.old_x, game.hero.old_y = game.hero.x, game.hero.y
    game.hero.x, game.hero.y = game.x, game.y
```

## Why Two Position Systems?

This dual-position system exists because:

1. **`Game.x/y`**: Direct position for game logic (pathfinding, collisions, etc.)
2. **`GameCharacter.x/y`**: Position wrapper that includes rendering info (sprites, images)

### Architecture
```
Game
├── x, y              (game logic position)
├── hero: GameCharacter
    ├── x, y          (rendering position)
    ├── entity: Character
        └── (no position - pure business logic)
```

The positions must be kept synchronized for the display to match the game state.

## Testing

### Before Fix
- ✗ Character moved (game.x/y changed)
- ✗ Screen showed character at old position (game.hero.x/y unchanged)
- ✗ Collision detection worked (uses game.x/y)
- ✗ Visual feedback broken

### After Fix
- ✅ Character moves (game.x/y changes)
- ✅ Screen updates to show new position (game.hero.x/y synchronized)
- ✅ Collision detection works (uses game.x/y)
- ✅ Visual feedback correct

## Similar Issues to Watch For

This pattern should be applied anywhere character position is modified:

1. ✅ `move_char()` - FIXED
2. ✅ `Game.__init__()` - Already synchronized on initialization
3. ⚠️ `update_level()` - Check if synchronization needed
4. ⚠️ Loading saved games - Check if positions are synchronized

## Related Code

### Initialization (already correct)
```python
# In Game.__init__()
self.hero = create_game_character(hero, x=hero_x, y=hero_y, ...)
# Game position tracking
self.x, self.y = self.hero.x, self.hero.y  # ✅ Synchronized
```

### Display (relies on hero.x/y)
```python
# In update_display()
game.hero.draw(screen, image, TILE_SIZE, *view_port_tuple)
# Uses game.hero.x and game.hero.y
```

## Lessons Learned

1. **Keep position state minimal**: Having two position systems increases complexity
2. **Always synchronize**: When one position changes, update the other
3. **Document coupling**: Make it clear when variables must be kept in sync
4. **Consider refactoring**: Could `game.x/y` be properties that read from `game.hero.x/y`?

## Potential Future Improvement

```python
# Option: Make game.x/y properties instead of attributes
class Game:
    @property
    def x(self) -> int:
        return self.hero.x
    
    @x.setter
    def x(self, value: int):
        self.hero.old_x = self.hero.x
        self.hero.x = value
    
    @property
    def y(self) -> int:
        return self.hero.y
    
    @y.setter
    def y(self, value: int):
        self.hero.old_y = self.hero.y
        self.hero.y = value
```

This would **eliminate the need for manual synchronization** by making `game.x/y` automatically read/write to `game.hero.x/y`.

## Conclusion

✅ **Problem solved** by synchronizing `game.hero.x/y` with `game.x/y` in the `move_char()` function.

The screen now correctly updates when the character moves, providing proper visual feedback to the player.

