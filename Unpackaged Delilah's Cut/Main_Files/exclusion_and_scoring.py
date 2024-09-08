"""
File that runs exclusion and scoring, as well as initial report generation


"""

import datetime
import Main_Files.settings as settings


# intake a list of RNA Objects, and a list of settings to exclude by and exclude them from list based on properties.
def basicExclusion(RNAObjs, settingsList):
    RNAs = RNAObjs.copy()

    keptRNAs = []
    excludedRNAs = []

    # Generates excluding list based on settings (list of dicts)
    boolIfNegExcluders = []
    for item in settingsList:
        if item["exclusionary"] == True and item["wantedVal"] == True:
            boolIfNegExcluders.append(item["propName"])

    boolIfPosExcluders = []
    for item in settingsList:
        if item["exclusionary"] == True and item["wantedVal"] == False:
            boolIfPosExcluders.append(item["propName"])

    for RNA in RNAs:

        # Excludes item i
        for item in boolIfNegExcluders:
            boolNeg = getattr(RNA, item)
            if boolNeg == False:
                RNA.reasonsExcluded.append(
                    item + " is " + str(boolNeg) + " and was thus excluded"
                )
                RNA.isExcluded = True

        for item in boolIfPosExcluders:
            boolPos = getattr(RNA, item)
            if boolPos == True:
                RNA.reasonsExcluded.append(
                    item + " is " + str(boolPos) + " and was thus excluded"
                )
                RNA.isExcluded = True

        if RNA.isExcluded == True:
            excludedRNAs.append(RNA)
        else:
            keptRNAs.append(RNA)

    return (keptRNAs, excludedRNAs)


# intake list of RNA objects (post exlusion), and list of dictionarys with 'propName', 'wantedVal' 'scoreVal', updates RNA Objects, returns same list
def scoreRNA(RNAObjs, ListODictBools):

    # Scoring RNAs, Out of 100
    for RNA in RNAObjs:
        potentialScore = 0
        RNAScore = 0

        for dict in ListODictBools:
            if dict["exclusionary"] == False:
                valName = dict["propName"]
                boolShouldBe = dict["wantedVal"]
                boolActual = getattr(RNA, valName)
                traitWeight = dict["scoreVal"]

                potentialScore += traitWeight
                if boolActual == boolShouldBe:
                    RNAScore += traitWeight

        ScorePer = round(100 * (RNAScore / potentialScore), 2)
        RNA.score = ScorePer
    return RNAObjs


# take in RNAList and return it sorted by score value
def bubbleSortRNAs(RNAObjs):

    n = len(RNAObjs)
    for i in range(n):
        for j in range(0, n - i - 1):
            if getattr(RNAObjs[j], "score") < getattr(RNAObjs[j + 1], "score"):
                RNAObjs[j], RNAObjs[j + 1] = RNAObjs[j + 1], RNAObjs[j]

    return RNAObjs


# Return top N inputs of RNA List
def topNRNAs(RNAObjs, n):

    settings.totalNonExcludedRNAs = len(RNAObjs)

    if len(RNAObjs) < n:
        return RNAObjs
    return RNAObjs[:n]


# Takes in List of RNA objects (scored) and returns full list of list of descriptive strings
def generateRNAreports(RNAObjs, settingsDict):
    listOfReports = []

    # NOTIFIES if no RNA FOund
    if len(RNAObjs) == 0:
        report = []
        report.append("________________________________________________________")
        report.append("________________________________________________________")
        report.append("NO VIABLE SIRNAs found (Exclusion Parameters too strict)")
        report.append("________________________________________________________")
        listOfReports.append(report)
        return listOfReports

    for RNA in RNAObjs:
        report = []
        report.append("________________________________")
        report.append("________________________________")
        report.append("REPORT for siRNA with sequence: 5'-" + RNA.sequence + "- 3'")
        report.append("________________________________")
        report.append("RNA length: " + str(RNA.length))
        report.append("RNA start position on mRNA: " + str(RNA.threePrimeSpot))
        report.append("RNA end position on mRNA: " + str(RNA.fivePrimeSpot))
        report.append("RNA score (out of 100): " + str(RNA.score))
        report.append("________________________________")

        report.append("______Scoring Information_______")
        report.append("________________________________")

        for item in settingsDict:
            if item["exclusionary"] == True:
                continue
            statement = item["question"] + str(getattr(RNA, item["propName"]))
            if getattr(RNA, item["propName"]) == item["wantedVal"]:
                statement += ", which is a positive"

                statement += (
                    ", resulting in + " + str(item["scoreVal"]) + " relative score"
                )

            else:
                statement += ", which is a negative"
                statement += (
                    ", resulting in missing "
                    + str(item["scoreVal"])
                    + " relative score"
                )

            report.append(statement)

        report.append("________________________________")
        report.append("")
        listOfReports.append(report)
    return listOfReports


def generateOverviewReport():
    report = []

    # Run Overview
    report.append("________________________________")
    report.append(
        'RUN OVERVIEW for run titled: "'
        + str(settings.basicNeedsDict["OutputFileName"])
        + '"'
    )
    if len(settings.userWarnings) != 0:
        report.append("IRREGULARITIES WITHIN THE RUN FOUND: ")
        for item in settings.userWarnings:
            report.append(item)
            report.append("________________________________")

    report.append(
        "Date and Time of run: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    report.append(
        "Number of non excluded siRNAs found: " + str(settings.totalNonExcludedRNAs)
    )

    report.append(
        f"How many of top siRNAs overviewed here: {settings.basicNeedsDict['HowManyRNAOutput']}"
    )
    report.append("________________________________")
    report.append("")
    report.append("________________________________")

    report.append("")
    # Sequence Information
    report.append("SEQUENCE INFORMATION")

    report.append("mRNA Sequence: ")

    length = len(settings.sequence_dict["sequence"])
    lineLen = 65
    quotient, remainder = divmod(length, lineLen)
    for i in range(quotient):
        if i == 0:
            report.append(
                "5' - "
                + settings.sequence_dict["sequence"][i * lineLen : (i + 1) * lineLen]
            )
        elif i == quotient and remainder == 0:
            report.append(
                settings.sequence_dict["sequence"][i * lineLen : (i + 1) * lineLen]
                + "- 3'"
            )
        else:
            report.append(
                settings.sequence_dict["sequence"][i * lineLen : (i + 1) * lineLen]
            )
    if remainder > 0:
        report.append(settings.sequence_dict["sequence"][-remainder:] + "- 3'")

    report.append("________________________________")
    report.append("")

    # Basic Needs Dict Overview
    report.append("Basic Run Settings Overview")
    report.append(
        f"Sequence Input Method: {'Text File' if settings.basicNeedsDict['textFile(T)/CopyPasted(F)'] else 'Direct Input'}"
    )
    report.append(
        f"Input Type: {'cDNA' if settings.basicNeedsDict['cDNA(T)/mRNA(F)'] else 'mRNA'}"
    )
    report.append(
        f"Min Length of siRNAs Generated: {settings.basicNeedsDict['minLengthChecked']}"
    )
    report.append(
        f"Max Length of siRNAs Generated: {settings.basicNeedsDict['maxLengthCHecked']}"
    )
    report.append(
        f"Run conducted with Default Parameters? {'Yes' if settings.basicNeedsDict['RunDefaultParam'] else 'No'}"
    )
    report.append(
        f"Save Settings for future use: {'Yes' if settings.basicNeedsDict['saveSettings'] else 'No'}"
    )
    report.append(f"Output File Name: {settings.basicNeedsDict['OutputFileName']}")
    report.append("________________________________")
    report.append("")

    # Exclusionary Parameters
    report.append("Overview of Parameters causing siRNA exclusion")
    report.append("________________________________")
    for param in settings.exclusionAndScoringDict:
        if param["exclusionary"]:
            opposite_val = not param["wantedVal"]
            report.append(
                f"{param['question']} If the answer was {opposite_val}, it was excluded."
            )
    report.append("________________________________")
    report.append("")

    # Scoring Parameters for Non-Exclusionary Items
    report.append("Scoring Parameters")
    for param in settings.exclusionAndScoringDict:
        if not param["exclusionary"]:
            score_info = f"{param['question']} Desired Answer: {param['wantedVal']}, Score if fullfilled: {param['scoreVal']}"
            report.append(score_info)
    report.append("________________________________")
    report.append("")

    # Sequence Options Overview
    report.append("Sequence Options Overview")
    report.append(
        f"How far from Start Codon to Search: {settings.sequenceOpt['howFarFromStartCodonInputSearch']} bases"
    )
    report.append(
        f"How near to Stop Codon to Search: {settings.sequenceOpt['howFarFromStopCodonInputSearch']} bases"
    )
    report.append(
        f"Organisms for Off-Target Considerations: {', '.join(settings.sequenceOpt['OrganismForOffTargets']) if settings.sequenceOpt['OrganismForOffTargets'] else 'None'}"
    )
    report.append("________________________________")

    return report
