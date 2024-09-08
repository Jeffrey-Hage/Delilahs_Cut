# File for storing all the global variables

import json
import os
import sys

"""
File that contains all the initial settings, and gets updated each instance upon modification

"""

userWarnings = []


totalNonExcludedRNAs = 0

# GUI Updated
sequence_dict = {"sequence": None, "file_name": None}

# GUI updated
basicNeedsDict = {
    "textFile(T)/CopyPasted(F)": False,
    "cDNA(T)/mRNA(F)": True,
    "minLengthChecked": 20,
    "maxLengthCHecked": 22,
    "HowManyRNAOutput": 10,
    "RunDefaultParam": False,
    "saveSettings": False,
    "OutputFileName": None,
}

# GUI Updated
exclusionAndScoringDict = [
    # Name of Parameter, is it exclusionary by default, if its exclusionary what value is passed, if not excluded what the score?
    {
        "propName": "isAllUnfolded",
        "exclusionary": True,
        "wantedVal": True,
        "scoreVal": 300,
        "question": "Is the siRNA Unfolded in solution? ",
    },
    {
        "propName": "hasUInPosOne",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 100,
        "question": "Does the siRNA have U in first position? ",
    },
    {
        "propName": "hasUOrAInPosOne",
        "exclusionary": True,
        "wantedVal": True,
        "scoreVal": 150,
        "question": "Does the siRNA have U OR A in first position? ",
    },
    {
        "propName": "hasGOrCInLastPos",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 80,
        "question": "Does the siRNA have a G or C in the last position? ",
    },
    {
        "propName": "GCWithinRange",
        "exclusionary": True,
        "wantedVal": True,
        "scoreVal": 200,
        "question": "Is GC content within accepted Range? ",
    },
    {
        "propName": "isPreferablyLoaded",
        "exclusionary": True,
        "wantedVal": True,
        "scoreVal": 200,
        "question": "Is the Antisense strand preferably Loaded? ",
    },
    {
        "propName": "withinmRNARange",
        "exclusionary": True,
        "wantedVal": True,
        "scoreVal": 150,
        "question": "Is the siRNA targeting a region within accepted area of mRNA? ",
    },
    {
        "propName": "loosemRNARegion",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 100,
        "question": "Is the mRNA region mostly unpaired? ",
    },
    {
        "propName": "fivePrimeLoosemRNA",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 50,
        "question": "Is the 5' region of the siRNA targeting an unpaired mRNA region? ",
    },
    {
        "propName": "threePrimeLoosemRNA",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 50,
        "question": "Is the 3' region of the siRNA targeting an unpaired mRNA region? ",
    },
    {
        "propName": "lowGCNineFourteen",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 50,
        "question": "Does the 9th-14th position contain less than 50 percent G and C? ",
    },
    {
        "propName": "hasAInTen",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 30,
        "question": "Does the siRNA have an A in 10th position? ",
    },
    {
        "propName": "hasUInSixteen",
        "exclusionary": False,
        "wantedVal": True,
        "scoreVal": 30,
        "question": "Does the siRNA have a U in the 16th position? ",
    },
    {
        "propName": "hasCytoMotif",
        "exclusionary": True,
        "wantedVal": False,
        "scoreVal": 100,
        "question": "Does the siRNA have a cytotoxic motif? ",
    },
    {
        "propName": "hasImmuneMotif",
        "exclusionary": True,
        "wantedVal": False,
        "scoreVal": 100,
        "question": "Does the siRNA have a Immune Motif? ",
    },
    {
        "propName": "hasNineGCinRow",
        "exclusionary": True,
        "wantedVal": False,
        "scoreVal": 100,
        "question": "Does RNA have nine G or C in a row? ",
    },
    {
        "propName": "hasGGG",
        "exclusionary": False,
        "wantedVal": False,
        "scoreVal": 80,
        "question": "Does the siRNA have a GGG sequence? ",
    },
    {
        "propName": "hasCCC",
        "exclusionary": False,
        "wantedVal": False,
        "scoreVal": 80,
        "question": "Does the siRNA have a CCC sequence? ",
    },
    {
        "propName": "hasCInSeven",
        "exclusionary": False,
        "wantedVal": False,
        "scoreVal": 30,
        "question": "Does the siRNA have a U in the 7th position? ",
    },
]


sequenceOpt = {
    "sequenceInp": None,
    "howFarFromStartCodonInputSearch": 75,
    "howFarFromStopCodonInputSearch": 50,
    "OrganismForOffTargets": [],
}


def saveDataJson(fileName):
    if "." not in fileName:
        fileName += ".json"

    # Get the full path to the settings file in 'Saved_Settings'
    path = get_settings_file_path(fileName)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = {
        "basicNeedsDict": basicNeedsDict,
        "sequence_dict": sequence_dict,
        "exclusionAndScoringDict": exclusionAndScoringDict,
        "sequenceOpt": sequenceOpt,
    }

    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def get_base_dir():
    """
    Returns the base directory of the executable. This will be the directory
    where the exe is located when packaged, or the script's directory in development.
    """
    if getattr(sys, "frozen", False):
        # The application is frozen (packaged by PyInstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        # The application is running as a normal Python script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return base_dir


def get_settings_file_path(filename):
    """
    Returns the path to the settings file in the 'Saved_Settings' directory.
    """
    base_dir = get_base_dir()
    return os.path.join(base_dir, "Saved_Settings", filename)
