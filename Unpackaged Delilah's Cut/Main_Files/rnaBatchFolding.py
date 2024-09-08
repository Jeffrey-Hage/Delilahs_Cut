"""
File called as a subproccess to return the folding of a group of siRNAs
Called like this because of incompatability of ViennaRNA and PyQT6 module upon packaging with pyinstaller, and no other workaround could be found.
This file is one of two reasons for the python installation requirement of the machine.

"""

import sys
import json
import RNA as folding
import tempfile
import os


def fold_rna(sequence):
    fold = folding.fold_compound(sequence)
    struct, energy = fold.mfe()
    return struct, energy


if __name__ == "__main__":
    # Read the input JSON from stdin
    input_data = json.loads(sys.stdin.read())

    # Prepare a list to store results
    results = []

    # Process each sequence
    for item in input_data:
        struct, energy = fold_rna(item["sequence"])
        item["struct"] = struct
        item["energy"] = round(float(energy), 2)
        results.append(item)

    # Write results to a temporary file
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".json"
    ) as tmp_file:
        json.dump(results, tmp_file)
        temp_file_path = tmp_file.name

    # Output the path to the temporary file to stdout (so the main process can read it)
    print(temp_file_path)
