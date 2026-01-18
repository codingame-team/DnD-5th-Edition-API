from collections import Counter


def is_solvable(cube):
    # Flatten cube to get all stickers in a single list
    stickers = ''.join(cube).replace(' ', '').replace('\n', '')

    # Check for exact color count: each color should appear exactly 9 times
    color_counts = Counter(stickers)
    if any(count != 9 for count in color_counts.values()):
        return "UNSOLVABLE"

    # Define pieces by extracting them from the cube layout
    edges = [
        stickers[1] + stickers[10], stickers[3] + stickers[12], stickers[5] + stickers[14], stickers[7] + stickers[16],
        stickers[19] + stickers[28], stickers[21] + stickers[30], stickers[23] + stickers[32], stickers[25] + stickers[34],
        stickers[37] + stickers[46], stickers[39] + stickers[48], stickers[41] + stickers[50], stickers[43] + stickers[52]
    ]

    corners = [
        stickers[0] + stickers[9] + stickers[20], stickers[2] + stickers[11] + stickers[18],
        stickers[6] + stickers[15] + stickers[24], stickers[8] + stickers[17] + stickers[26],
        stickers[36] + stickers[45] + stickers[29], stickers[38] + stickers[47] + stickers[27],
        stickers[42] + stickers[51] + stickers[33], stickers[44] + stickers[53] + stickers[35]
    ]

    # Check all edge pieces for exactly two unique colors
    for edge in edges:
        if len(set(edge)) != 2:
            return "UNSOLVABLE"

    # Check all corner pieces for exactly three unique colors
    for corner in corners:
        if len(set(corner)) != 3:
            return "UNSOLVABLE"

    return "SOLVABLE"


# Example usage with an input cube pattern
cube = [
    "    UUU",  # Up face
    "    UUU",
    "    UUU",
    "LLL FFF RRR BBB",  # Middle layer (Left, Front, Right, Back faces)
    "LLL FFF RRR BBB",
    "LLL FFF RRR BBB",
    "    DDD",  # Down face
    "    DDD",
    "    DDD"
]

print(is_solvable(cube))
