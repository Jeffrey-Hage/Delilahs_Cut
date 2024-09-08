
# The Short of It
siRNA is a powerful tool for mRNA and protein knockdown. Delilah's Touch aims to enable researchers to generate effective siRNA sequences quickly and easily, while leaving a lot of options in the researchers hands.

## Background
siRNA has had a significant impact since its development, following the revolutionary discovery of the native miRNA pathway in various organisms. siRNAs opened new avenues for research by allowing control over targeted mRNA and protein levels through simple design. Years of research have gone into optimizing gene knockdown using siRNA, with a focus on a variety of key design components. The field has since advanced to chemically modified siRNAs, which enhance stability and knockdown efficiency. However, these modifications can sometimes reduce interactions with the RISC complex, depending on the specific changes.

Many findings from decades of siRNA research remain relevant to the design of chemically modified siRNAs, though the exact impact of each design parameter likely depends on the specific modifications used. Even for unmodified siRNAs, the relative importance of different design features is still debated. Delilah's Cut aims to assist researchers in designing both types of siRNA and provides the foundational step in this process.

## Delilah’s Cut’s Approach
Researchers have explored various characteristics of siRNA to determine what makes them effective. Some findings are robust, grounded in mechanistic evidence, such as those related to preferential strand loading and avoiding stable secondary structures. Other findings, like the effects of specific nucleotides at certain positions, are less consistent.

Delilah’s Cut empowers researchers to tailor siRNA design to their needs, preferences, and expertise. While the program offers a recommended set of design preferences based on research findings, it allows flexibility in adjusting weighting and exclusion parameters. Delilah’s Cut also prioritizes a user-friendly experience.

## How the Program Works
Delilah’s Cut first gathers all user preferences through the interface, including parameters for siRNA generation, sequence information, and file names. Users can also adjust exclusion and screening criteria if the “Use Default Settings” option is unchecked. The sequence is then processed (with non-relevant characters removed, retaining only the bases) and sent to the backend.

The program generates all possible siRNAs within the specified length range and filters out those not meeting the exclusion criteria. The remaining siRNAs are then scored based on either the customized or default settings, sorted, and summarized in a report.

Please note that siRNAs commonly have overhangs, but this program generates only the complementary sequences for each region. Overhangs can be added manually after generation.

## Future Directions
Future versions may incorporate automatic BLAST transcriptome searches, which are currently excluded due to computational intensity. Another potential improvement would be to adjust the weighting parameters using a machine learning model trained on a relevant database. Unfortunately, most major siRNA databases are outdated and no longer accessible. If you have access to an up-to-date siRNA effectiveness database, please contact the email below. Future expansions of detecting additional siRNA aspects are also on their way, as well as usability and quality of life improvements (such as removing python as a requirement).

## Authorship
This program was created by Jeffrey Hage, who holds a Bachelors in Biochemistry from CU Boulder. You can contact him via email at Jeffrey.Hage@colorado.edu.

## Sources
Rationale for relevant parameters is based on the following studies:

- Tafer, H. Bioinformatics of siRNA Design. in RNA Sequence, Structure, and Function: Computational and Bioinformatic Methods (eds. Gorodkin, J. & Ruzzo, W. L.) 477–490 (Humana Press, Totowa, NJ, 2014). doi:10.1007/978-1-62703-709-9_22.
- Gredell, J. A., Berger, A. K. & Walton, S. P. Impact of target mRNA structure on siRNA silencing efficiency: a large-scale study. Biotechnol Bioeng 100, 744–755 (2008).
- Petri, S. & Meister, G. siRNA Design Principles and Off-Target Effects. in Target Identification and Validation in Drug Discovery: Methods and Protocols (eds. Moll, J. & Colombo, R.) 59–71 (Humana Press, Totowa, NJ, 2013). doi:10.1007/978-1-62703-311-4_4.
- Friedrich, M. & Aigner, A. Therapeutic siRNA: State-of-the-Art and Future Perspectives. BioDrugs 36, (2022).
