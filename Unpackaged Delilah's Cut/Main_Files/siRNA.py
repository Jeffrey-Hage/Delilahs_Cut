""""
siRNA file contains the siRNA object and the functions for evaluating its score
ex: Is there an A or U in postition 1?


In order to add a new function, all you need to do is Create a function to evaluate the quality, and then add that property into the settings.py file dictionary "exclusionAndScoringDict".
 The program will handle everything else including implimentation to GUI



"""

# imports
import subprocess
import os
import sys
import Main_Files.settings as settings

# RNA Class, containing all information about the RNA


class siRNAObj:
    def __init__(
        self,
        seq,
        threePrimemRNAPos,
        fivePrimemRNAPos,
        parentMRNA=None,
        energy=None,
        structure=None,
    ):
        # Initialization of RNA
        self.parentMRNA = parentMRNA

        # Basic RNA qualities generation
        self.length = len(seq)
        self.sequence = seq

        self.struct = structure
        self.mfe = energy

        """ Important metrics for siRNA viability"""

        self.threePrimeSpot = threePrimemRNAPos
        self.fivePrimeSpot = fivePrimemRNAPos

        self.GCcontent()  # see self.GCPer
        self.basePairs()  # see self.basePairsNum

        # -1 to 1 values, positive is favored
        self.fivePrimeLooseness()  # see self.selectiveLoading

        # Boolean attributes, positve
        self.isUnfolded()  # see self.isAllUnfolded
        self.startWithU()  # see self.hasUInPosOne
        self.startWithUorA()  # see self.hasUOrAInPosOne
        self.endsWithGOrC()  # see self.hasGOrCInLastPos
        self.GCInRange()  # see self.GCWithinRange

        self.isPrefLoaded()  # see self.isPreferablyLoaded

        self.withinMRNARange()  # see self.withinmRNARange
        self.withinLooseMRNARegion()  # see self.loosemRNARegion
        self.fivePrimeEndOnLoosemRNA()  # see self.fivePrimeLoosemRNA
        self.threePrimeEndOnLoosemRNA()  # see self.threePrimeLoosemRNA
        self.lowGCinNinetoFourteen()  # see self.lowGCNineFourteen

        # Additional Positional Params, Positive
        self.AInTen()  # see self.hasAInTen
        self.UInSixteen()  # see self.hasUInSixteen

        # Boolean attributes, negative
        self.cytoMotif()  # see self.hasCytoMotif
        self.immuneMotif()  # see self.hasImmuneMotif
        self.gcsInRow()  # see self.hasNineGCinRow

        self.hasGGGseq()  # see self.hasGGG
        self.hasCCCseq()  # see self.hasCCC

        # Additional Positional Params, Negative
        self.CInSeven()  # see self.hasCInSeven

        # list of reasons that siRNA was excluded from dataset
        self.isExcluded = False
        self.reasonsExcluded = []

        # Score of siRNA 0-100
        self.score = None

    def CInSeven(self):
        value = False
        if len(self.sequence) < 7:
            self.hasCInSeven = value
            return

        if self.sequence[6] == "c":
            value = True
        self.hasCInSeven = value

    def UInSixteen(self):
        value = False
        if len(self.sequence) < 16:
            self.hasUInSixteen = value
            return

        if self.sequence[15] == "u":
            value = True
        self.hasUInSixteen = value

    def AInTen(self):
        value = False
        if len(self.sequence) < 10:
            self.hasAInTen = value
            return

        if self.sequence[9] == "a":
            value = True
        self.hasAInTen = value

    def hasCCCseq(self):
        Value = False
        if "ccc" in self.sequence:
            Value = True
        self.hasCCC = Value

    def hasGGGseq(self):
        Value = False
        if "ggg" in self.sequence:
            Value = True
        self.hasGGG = Value

    def lowGCinNinetoFourteen(self):
        value = False
        if len(self.sequence) < 15:
            self.lowGCNineFourteen = value
            return
        region = self.sequence[8:14]
        lengthRegion = len(region)
        GCs = 0
        for char in region:
            if char == "g" or char == "c":
                GCs += 1

        if GCs / lengthRegion < 0.5:
            value = True
        self.lowGCNineFourteen = value

    def fivePrimeEndOnLoosemRNA(self):
        value = True
        parentStruct = self.parentMRNA.struct
        localStruct = parentStruct[self.fivePrimeSpot - 3 : self.fivePrimeSpot]
        if "(" in localStruct or ")" in localStruct:
            value = False

        self.fivePrimeLoosemRNA = value

    def threePrimeEndOnLoosemRNA(self):
        value = True
        parentStruct = self.parentMRNA.struct
        localStruct = parentStruct[self.threePrimeSpot - 1 : self.threePrimeSpot + 2]
        if "(" in localStruct or ")" in localStruct:
            value = False

        self.threePrimeLoosemRNA = value

    # Check to make sure this works
    def withinLooseMRNARegion(self):
        value = True
        parentStruct = self.parentMRNA.struct
        localStruct = parentStruct[self.threePrimeSpot - 1 : self.fivePrimeSpot]
        lengthOfStruct = len(localStruct)
        pairedCount = 0
        for char in localStruct:
            if char == "(" or char == ")":
                pairedCount += 1
        if pairedCount / lengthOfStruct > 0.5:
            value = False
        self.loosemRNARegion = value

    def withinMRNARange(self):
        value = True
        if (
            self.fivePrimeSpot
            < self.parentMRNA.startCodonPos
            + settings.sequenceOpt["howFarFromStartCodonInputSearch"]
        ):
            value = False
        if self.threePrimeSpot > (
            self.parentMRNA.stopCodonPos
            - settings.sequenceOpt["howFarFromStopCodonInputSearch"]
        ):
            value = False
        self.withinmRNARange = value

    def isPrefLoaded(self):
        value = False
        if self.selectiveLoading > 0:
            value = True
        self.isPreferablyLoaded = value

    def __str__(self):
        # Object identified as sequence
        return self.sequence

    def GCInRange(self):
        value = False
        if self.GCPer > 0.30 and self.GCPer < 0.65:
            value = True
        self.GCWithinRange = value

    def endsWithGOrC(self):
        value = False
        if self.sequence[-1] == "g" or self.sequence[-1] == "c":
            value = True
        self.hasGOrCInLastPos = value

    def startWithUorA(self):
        value = False
        if self.sequence[0] == "u" or self.sequence[0] == "a":
            value = True
        self.hasUOrAInPosOne = value

    def startWithU(self):
        value = False
        if self.sequence[0] == "u":
            value = True
        self.hasUInPosOne = value

    # Checks if RNA fav conformation is unfolded
    def isUnfolded(self):
        value = False
        if self.basePairsNum == 0:
            value = True
        self.isAllUnfolded = value

    # rates relative stability of selective Loading of antisense strand
    def fivePrimeLooseness(self):
        fiveSeq = self.sequence[:3]
        threeSeq = self.sequence[-3:]
        score = 0

        stable = ["g", "c"]
        instable = ["a", "u"]
        for char in fiveSeq:
            if char in instable:
                score += 1
            else:
                score -= 1
        for char in threeSeq:
            if char in stable:
                score += 1
            else:
                score -= 1
        score = round(score / 6, 2)

        self.selectiveLoading = score

    # check if more than 9 gcs in a row
    def gcsInRow(self):
        gcs = 0
        hitMoreThanNine = False
        for char in self.sequence:
            if gcs >= 9:
                hitMoreThanNine = True

            if char == "g" or char == "c":
                gcs += 1
            else:
                gcs = 0
        self.hasNineGCinRow = hitMoreThanNine

    # check immune Motif
    def immuneMotif(self):
        Value = False
        if "guccuucaa" in self.sequence or "ugugu" in self.sequence:
            Value = True
        self.hasImmuneMotif = Value

    # check cyto motif
    def cytoMotif(self):
        Value = False
        if "uggc" in self.sequence:
            Value = True
        self.hasCytoMotif = Value

    # sets GC percentage
    def GCcontent(self):
        GCCount = 0
        for char in self.sequence:
            if char == "g" or char == "c":
                GCCount += 1
        self.GCPer = round(GCCount / self.length, 2)

    def basePairs(self):
        # counts base pairs based on parenthesis
        pairCount = 0
        for char in self.struct:
            if char == "(":
                pairCount += 1
        self.basePairsNum = pairCount
