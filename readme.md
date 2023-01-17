# Merge-PGN

A simple tool for merging several pgn games into a single pgn with one
game including all moves as variations.

Based on [merge-pgn](https://github.com/permutationlock/merge-pgn) with the addition of handling comments.

Requires you to have [python-chess](https://python-chess.readthedocs.io)
installed.

```
pip install python-chess
```

Example:
```
python merge-pgn.py "game1.pgn" "game2.pgn" "games3-7.pgn" > "all_games.pgn"
```

Or, one PGN with multiple games:
```
python merge-pgn.py "games.pgn" > "all_games_merged.pgn"
```

## Comments

Merging of comments (including annotations like arrows and circles) are supported
with a few caveats. But in general it works like this.

The following to PGN's:

```
1.e4 e5 { This is the first comment } {[%cal Gf2f5][%csl Gb3]}
```

```
1.e4 e5 { This is the second comment } {[%cal Ye2e3][%csl Yc4]}
```

..would be combined into this:

```
1.e4 e5 { This is the first comment

This is the second comment } { [%cal Gf2f5,Ye2e3][%csl Gb3,Yc4] }
```

Ie, normal text comments are merged and separated by two newlines. Identical comments 
are not duplicated.

## Caveats

One might argue that comments should be merged into completely separate {} sections. The PGN standard is vague on this, but most tools do it in this way. However because of a limitation in the chess.pgn library that this tool uses 
(https://github.com/niklasf/python-chess) that was discussed at 
https://github.com/niklasf/python-chess/discussions/945 and 
https://github.com/niklasf/python-chess/issues/946 only annotations ([%cal] and [%csl] etc) have been completely separated into separate {}'s, and even that in a kind of hacky solution.

## Changelog

### 2023-01-17

- Bugfix: Fixed a problem where multiple arrows of different colors were all kept. Now only the first encountered arrow in a specific location is kept.
- Feature: Headers that are identical in all games being merged are kept, and only those that are not common are left empty.

### 2023-01-08

- First modified version after forking https://github.com/permutationlock/merge-pgn.
