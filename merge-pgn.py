# Description: A simple tool to merge several pgn games into a single game with
# variations.

import chess.pgn
import sys
import re
from collections import OrderedDict

def extract_annotations(text):
    annotations = OrderedDict()
    normal_text = ""

    # Split the text by placeholders
    parts = re.split(r"\[|\]", text)
    for i, part in enumerate(parts):
        # Check if the current part is a placeholder
        if part and part[0] == "%":
            # Split the part by the white space
            key, values = part.split(" ", 1)
            # Split the values by the comma and strip any leading/trailing whitespace
            values = [value.strip() for value in values.split(",")]
            # Add the values to the annotations dictionary
            if key not in annotations:
                annotations[key] = OrderedDict()
            for value in values:
                annotations[key][value] = None

        else:
            # Add the part to the normal_text variable
            normal_text += part

    # Replace multiple consecutive spaces with a single space in the normal_text variable
    normal_text = re.sub(r"\ ", " ", normal_text)

    return normal_text, annotations

def merge_text_strings(text1, text2):
    # If one is included in the other then it's a duplicate comment and should be ignored
    one_in_two = text1 and text2 and text1 in text2
    two_in_one = text1 and text2 and text2 in text1
    combined_text = ""

    combined_text += text1
    if text1 and text2:
        combined_text += "\n\n"
    combined_text += text2

    return combined_text

def merge_comments(text1, text2):
    normal_text1, annotations1 = extract_annotations(text1)
    normal_text2, annotations2 = extract_annotations(text2)

    # Concatenate the two normal_text variables separated by two newlines
    combined_text = merge_text_strings(normal_text1, normal_text2)

    # Merge the values of the annotation maps together
    for key, values in annotations2.items():
        if key not in annotations1:
            annotations1[key] = OrderedDict()
        for value in values:
            annotations1[key][value] = None

    # Format the merged annotations in the same way the placeholders appear in the text
    formatted_annotations = ""
    for key, values in annotations1.items():
        formatted_annotations += f"[{key} {','.join(values.keys())}]"

    return combined_text, formatted_annotations

def insert_braces(text):
    # Find all the occurrances of the braced string using re.finditer
    brace_matches = list(re.finditer(r'\{(.*?)\}', text, flags=re.DOTALL))

    # Iterate through all the matches (in reversed order because inserting stuff messes up the matches completely)
    for brace_match in reversed(brace_matches):
        start_pos = brace_match.start()
        end_pos = brace_match.end()

        # Find the position of the first [% within the braces
        percent_match = re.search(r'\[%', brace_match.group(1), flags=re.DOTALL)
        if percent_match is None:
            continue

        percent_pos = percent_match.start() + start_pos + 1

        comment_text = text[start_pos + 1:percent_pos].strip()

        # Insert "} {" at the position of the [% , if and only if the text before is non-empty
        if comment_text:
            text = text[:percent_pos] + "} { " + text[percent_pos:]

    return text

def main():
    try:
        args = sys.argv[1:]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <string_to_reverse>")

    master_node = chess.pgn.Game()

    games = []
    for name in args:
        pgn = open(name, encoding="utf-8-sig")
        game = chess.pgn.read_game(pgn)
        while game is not None:
            text, annotations = merge_comments(master_node.comment, game.comment)
            master_node.comment = f"{text}{annotations}"

            games.append(game)
            game = chess.pgn.read_game(pgn)

    mlist = []
    for game in games:
        mlist.extend(game.variations)

    variations = [(master_node, mlist)]
    done = False

    while not done:
        newvars = []
        done = True
        for vnode, nodes in variations:
            newmoves = {}  # Maps move to its index in newvars.
            for node in nodes:
                if node.move is None:
                    continue
                elif node.move not in list(newmoves):
                    nvnode = vnode.add_variation(node.move, nags = node.nags)
                    text, annotations = merge_comments(node.comment, "")
                    nvnode.comment = f"{text}{annotations}"

                    if len(node.variations) > 0:
                        done = False
                    newvars.append((nvnode, node.variations))
                    newmoves[node.move] = len(newvars) - 1
                else:
                    nvnode, nlist = newvars[newmoves[node.move]]
                    text, annotations = merge_comments(nvnode.comment, node.comment)
                    nvnode.comment = f"{text}{annotations}"
                    nvnode.nags.update(node.nags)

                    if len(node.variations) > 0:
                        done = False
                    nlist.extend(node.variations)
                    newvars[newmoves[node.move]] = (nvnode, nlist)
        variations = newvars

    pgn = f"{master_node}"

    # Workaround to make sure the annotations end up in their own curly brackets,
    # ie 1.e4 { A comment } { [%cal Ge2e4] }    instead of    1.e4 { A comment [%cal Ge2e4] }
    pgn = insert_braces(pgn)
    
    print(pgn)


main()