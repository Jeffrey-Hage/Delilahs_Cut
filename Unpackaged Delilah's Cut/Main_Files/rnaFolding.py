"""
File called as a subproccess to return the folding of an RNA
Called like this because of incompatability of ViennaRNA and PyQT6 module upon packaging with pyinstaller, and no other workaround could be found.
This file is one of two reasons for the python installation requirement of the machine.

"""

import sys

import RNA as folding


def fold_rna(sequence):
    fold = folding.fold_compound(sequence)
    struct, energy = fold.mfe()
    return struct, energy


if __name__ == "__main__":
    # The RNA sequence is passed as a command-line argument
    sequence = sys.argv[1]
    struct, energy = fold_rna(sequence)

    # Output the structure and energy to be captured by the main program
    print(f"{struct}|{energy}")
