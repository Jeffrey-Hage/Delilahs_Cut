
# Overall Process
Delilah’s Cut requires just a few inputs from you: some settings, an output file name, and a sequence. From there, the program will handle everything else, including generating siRNAs, ranking them, and creating your report.

## Settings - Basic Parameters
First, click the "Begin Analysis" screen, where you will see various basic options for your run. Choose whether you will input your sequence directly or have the program read it from a file. If you choose to read from a file, ensure it is a “.txt” file located in the sequence input folder. The program will ignore any characters in either input method that are not A, C, G, T, or U bases.
On this page, you can also choose to run with default parameters or customize the settings. If you uncheck the "Default Parameters" option, the program will guide you to additional pages where you can further refine your settings. You can also opt to save your settings for future use. You can also choose to load settings from a previous run, you can see your options in the "Saved_Settings" Folders. Exclude the file suffix when loading.

## Settings - Exclusionary Parameters
On the Exclusionary Parameters page, you can check or uncheck boxes to determine if certain aspects of an RNA sequence should exclude it from the analysis. This page explains each parameter and identifies which values would be considered undesirable, leading to exclusion if selected. The checkboxes are set to their default positions.

## Settings - Scoring Parameters
On the Scoring Parameters page, you will find all non-exclusionary criteria listed. Here, you can adjust the relative weights for scoring from 0 to 500. Exclusionary parameters do not contribute to scoring since all RNA sequences must already meet these criteria. The scoring values are initially set to their default positions. If you wish to ignore a parameter, set its slider to zero.

## Sequence Input
On the Sequence Input page, you will either see a sequence input textbox or a textbox to specify the file path. If using a file, include “.txt” in the file name. Sequences can be input in uppercase or lowercase but must be in the 5’-3’ orientation. The program assumes there are no introns in the mRNA or cDNA. Any characters that are not A, C, G, T, or U will be ignored. After entering your sequence or file name, specify your output file name. Do not include any suffixes, spaces, periods, or file extensions—these will be added automatically. Then, simply click "Begin Generating siRNAs" and wait for the program to process.

## Results of Analysis
On the results page, you can view a summary of the settings used in the run as well as the results. When you click the "Save as PDF" button, the PDF will be saved to the “Output_PDFs” folder within Delilah’s Cut, where you can access it in the future.
