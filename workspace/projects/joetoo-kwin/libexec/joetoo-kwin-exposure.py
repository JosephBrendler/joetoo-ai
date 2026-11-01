#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frame-rectangle exposure prediction, not compositor hit-test verification."""
import sys


def exposed(rect, above, n):
    x, y, w, h = rect
    if w < n or h < n:
        return False
    # Search candidate square origins at rectangle edges. For each horizontal
    # position, sweep forbidden vertical intervals instead of testing a cubic
    # grid of all X/Y combinations against all occluders.
    xs = {x, x + w - n}
    for a, b, c, d in above:
        xs.update((a - n, a + c))
    for a in xs:
        if not x <= a <= x + w - n:
            continue
        intervals = sorted((b - n, b + d) for c, b, e, d in above
                           if a < c + e and a + n > c)
        candidate = y
        for low, high in intervals:
            if low >= candidate:
                break
            if candidate < high:
                candidate = high
        if candidate <= y + h - n:
            return True
    return False



def main():
    n = int(sys.argv[1])
    rows = [line.split() for line in sys.stdin if line.strip()]
    for i, row in enumerate(rows):
        desktop, layer, slot = row[:3]
        if layer == 'panel':
            continue
        rank = {'under': 0, 'panel': 1, 'over': 2}
        higher = [list(map(int, other[3:])) for j, other in enumerate(rows)
                  if other[0] == desktop and (rank[other[1]], j) > (rank[layer], i)]
        if not exposed(list(map(int, row[3:])), higher, n):
            print(f'desktop [{desktop}] slot [{slot}]: overlap; desired {n}x{n} logical-pixel exposure cannot be maintained')


if __name__ == '__main__':
    main()
