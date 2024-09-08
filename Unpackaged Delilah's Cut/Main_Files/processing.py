"""
File handles initial processing of mRNA and generation of siRNAs
Also handles the calling of subprocesses (one of the reasons for python installation dependencies)


"""

from Main_Files.siRNA import *
import os
import sys
import Main_Files.settings as settings
import json


class MRNA:
    def __init__(
        self,
        seq=None,
        fivePrimePosOnGenome=None,
        threePrimePosOnGenome=None,
        organism=None,
    ):
        pass

    # Generates a list of all sequences as RNA Objects
    def generatesiRNASeq(self, minLength=20, maxLength=20, samp="Total"):

        mRNA = self.sequence
        if samp != "Total":
            # Case of when theres straight up too many sequences and need dif sampling method, implement later
            pass

        revCompmRNA = self.reverseCompSeq
        lengthList = [i for i in range(minLength, maxLength + 1)]
        mRNALen = len(mRNA)

        siRNADicts = []

        for length in lengthList:
            for pos in range(1 + mRNALen - length):
                siRNA = revCompmRNA[pos : pos + length]

                threePrimePosOnmRNA = mRNALen - (pos + length - 1)
                fivePrimePosOnmRNA = threePrimePosOnmRNA + length - 1

                siRNADicts.append(
                    {
                        "sequence": siRNA,
                        "threePrimePosOnmRNA": threePrimePosOnmRNA,
                        "fivePrimePosOnmRNA": fivePrimePosOnmRNA,
                        "struct": None,
                        "energy": None,
                    }
                )

        updatedsiRNADict = self.runSubprocess1(siRNADicts)
        # Function that calls a subprocess to retrieve all the structures and adds them to the dictionary appropriately,

        siRNAList = []
        for item in updatedsiRNADict:
            item["parentMRNA"] = self
            siRNAList.append(
                siRNAObj(
                    item["sequence"],
                    item["threePrimePosOnmRNA"],
                    item["fivePrimePosOnmRNA"],
                    parentMRNA=item["parentMRNA"],
                    energy=item["energy"],
                    structure=item["struct"],
                )
            )

        self.siRNAlist = siRNAList

        return siRNAList

    # Returns reverse compliment of RNA also 5' to 3', called by generatesiRNAseq
    def revComp(self):
        mRNA = self.sequence
        revComp = []
        for char in mRNA:
            match char:
                case "a":
                    revComp.append("u")
                case "u":
                    revComp.append("a")
                case "c":
                    revComp.append("g")
                case "g":
                    revComp.append("c")
        revComp.reverse()
        revCompStr = ""
        for char in revComp:
            revCompStr += char
        return revCompStr

    def findStartCodon(self):
        mRNA = self.sequence
        for i in range(len(mRNA)):
            if mRNA[i : i + 3] == "aug":
                return i + 1
        settings.userWarnings.append(
            "START CODON NOT FOUND, POSITION SET AT FIRST BASE"
        )
        return 1

    def findStopCodon(self):
        mRNA = self.sequence
        if "START CODON NOT FOUND, POSITION SET AT FIRST BASE" in settings.userWarnings:
            settings.userWarnings.append(
                "STOP CODON NOT FOUND, POSITION SET AT LAST SPOT"
            )
            return len(mRNA) - 4

        startCodonIndex = self.startCodonPos - 1
        possibleCodons = int(round((len(mRNA) - startCodonIndex) / 3, 1))
        for i in range(1, possibleCodons):

            codon = mRNA[startCodonIndex + (3 * i) : (startCodonIndex + (3 * i)) + 3]
            if codon == "uaa" or codon == "uag" or codon == "uga":
                return startCodonIndex + (3 * i) + 1

        settings.userWarnings.append("STOP CODON NOT FOUND, POSITION SET AT LAST SPOT")
        return len(mRNA) - 4

    # Function that intializes mRNA seq either through input or TXT file, and also calls relevant functions to generate qualities

    def getMRNA(self):

        if not settings.basicNeedsDict[
            "textFile(T)/CopyPasted(F)"
        ]:  # Checks if sequence was copy-pasted or needs to run text file
            mRNA = settings.sequence_dict["sequence"]
        else:
            try:
                f = settings.sequence_dict["file_name"]

                path = get_input_file_path(f)

                with open(path, "r") as fil:
                    # Read file and remove newlines
                    mRNA = fil.read().replace("\n", " ")
            except FileNotFoundError:
                sys.exit("File not found. Please check the file name and try again.")

        self.inputtedSequence = mRNA

        if settings.basicNeedsDict["cDNA(T)/mRNA(F)"] == True:
            mode = "cDNA"
        else:
            mode = "mRNA"
        mRNA = self.mRNAProcess(mode=mode)

        self.sequence = mRNA
        settings.sequence_dict["sequence"] = mRNA

        self.sequenceLength = len(mRNA)
        self.reverseCompSeq = self.revComp()
        self.struct = "set"
        # gives as absolute position of A within AUG, not the index
        self.startCodonPos = self.findStartCodon()
        self.stopCodonPos = self.findStopCodon()
        return
        # structure setter and getter

    @property
    def struct(self):
        return self._struct

    @struct.setter
    def struct(self, set="set"):
        self.runSubprocess()

    def runSubprocess(self):
        if getattr(sys, "frozen", False):
            # Get the correct path to rnaFolding.py in the frozen app
            script_path = os.path.join(sys._MEIPASS, "rnaFolding.py")
        else:
            script_path = os.path.join(os.path.dirname(__file__), "rnaFolding.py")

        # Use Popen to directly call the script
        process = subprocess.Popen(
            [
                "python",
                script_path,
                self.sequence,
            ],  # Use 'python' instead of sys.executable
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()

        if error:
            print(f"Error in RNA folding subprocess: {error.decode()}")
        else:
            struct, energy = output.decode().strip().split("|")
            self._struct = struct
            self.mfe = round(float(energy), 2)

    def runSubprocess1(self, siRNADicts):
        if getattr(sys, "frozen", False):
            # Get the correct path to rnaBatchFolding.py in the frozen app
            script_path = os.path.join(sys._MEIPASS, "rnaBatchFolding.py")
        else:
            script_path = os.path.join(os.path.dirname(__file__), "rnaBatchFolding.py")

        # Convert the siRNADicts list to a JSON string to pass it to the subprocess
        input_data = json.dumps(siRNADicts)

        # Call the subprocess and pass the input via stdin
        process = subprocess.Popen(
            [
                "python",
                script_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Send the JSON data to the subprocess and get the output path to the temp file
        output, error = process.communicate(input=input_data.encode())

        if error:
            print(f"Error in RNA folding subprocess: {error.decode()}")
            return None
        else:
            # Read the temp file path from the output
            temp_file_path = output.decode().strip()

            # Read the results from the temporary file
            with open(temp_file_path, "r") as tmp_file:
                updated_siRNADicts = json.load(tmp_file)

            # Clean up the temporary file after reading
            os.remove(temp_file_path)

            return updated_siRNADicts

    # Gets rid of non-GACU chars and warns if theres too much garbage
    def mRNAProcess(self, mode="mRNA"):

        mRNA = self.inputtedSequence.lower()
        output = ""
        removedChars = ""
        if mode == "mRNA":
            acceptableChars = {"a", "c", "g", "u"}
            for char in mRNA:
                if char in acceptableChars:
                    output += char
                else:
                    removedChars += char
            if "t" in removedChars:
                settings.userWarnings.append(
                    "mRNA Chosen, but sequence contained T, which was removed"
                )

        elif mode == "cDNA":
            acceptableChars = {"a", "c", "g", "t"}
            for char in mRNA:
                if char in acceptableChars:
                    if char == "t":
                        output += "u"
                    else:
                        output += char
                else:
                    removedChars += char
            if "u" in removedChars:
                settings.userWarnings.append(
                    "cDNA Chosen, but sequence contained U, which was removed"
                )

        return output


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


def get_input_file_path(filename):
    """
    Returns the path to the input file in the 'Sequence_Inputs' directory.
    """
    base_dir = get_base_dir()
    return os.path.join(base_dir, "Sequence_Inputs", filename)
