from typing import List


def in_view_range(start_x: int, start_y: int, target_x: int, target_y: int, obstacles: List[tuple]):
    if start_y < target_y:
        return bresenham_forward(start_x, start_y, target_x, target_y, obstacles)
    else:
        return bresenham_backward(start_x, start_y, target_x, target_y, obstacles)


def bresenham_forward(start_x: int, start_y: int, target_x: int, target_y: int, obstacles: List[tuple]):
    x0, y0, x1, y1 = start_x, start_y, target_x, target_y

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy
    current_x, current_y = x0, y0

    while True:
        e2 = 2 * err
        if e2 > -1 * dy:
            err -= dy
            current_x += sx

        if e2 < dx:
            err += dx
            current_y += sy

        if current_x == x1 and current_y == y1:
            break

        if (current_x, current_y) in obstacles:
            return False

    return target_x, target_y


def bresenham_backward(start_x: int, start_y: int, target_x: int, target_y: int, obstacles: List[tuple]):
    x0, y0, x1, y1 = target_x, target_y, start_x, start_y

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy
    current_x, current_y = x0, y0

    while True:
        e2 = 2 * err
        if e2 > -1 * dy:
            err -= dy
            current_x += sx

        if e2 < dx:
            err += dx
            current_y += sy

        if current_x == x1 and current_y == y1:
            break

        if (current_x, current_y) in obstacles:
            return False

    return target_x, target_y
