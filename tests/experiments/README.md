# Experiment: Evaluating Gene Implication in Ataxia Using `gen_analysis`

## Background

## Summary

## Purpose
Determine if the program `gen_analysis` correctly identifies known ataxia-associated genes from the `Chicago_Ataxia_Exome_Gene_List.tsv`. Since all input genes are involved in ataxia, the expected outcome is a 100% accuracy.

## Scope

### Acceptance Criteria
- The `gen_analysis.py` script must correctly identify 100% of the known ataxia-associated genes listed in the `Chicago_Ataxia_Exome_Gene_List.tsv` file.
- Any deviation from 100% accuracy will be considered a failure of the experiment.
- The results should be reproducible, meaning that running the script multiple times under the same conditions should yield the same 100% accuracy.
- Detailed logs or records of the script's output should be maintained to verify the accuracy of the results.
- The experiment will be considered successful only if all known ataxia genes are identified without any false negatives.

## Materials
- `Chicago_Ataxia_Exome_Gene_List.tsv` file containing known ataxia genes.
- Access to the `gen_analysis.py` script.
- A computational system to run the script.
- Logging or data collection software to record outcomes.

## Methodology
- The experiment will involve running the `gen_analysis.py` script using `Chicago_Ataxia_Exome_Gene_List.tsv` file as the input data.
- Positive identification of ataxia-associated genes will be determined by checking the output of `gen_analysis.py` for specific keywords or phrases indicating ataxia implication.
- The results will be collected and analyzed to ensure that all known ataxia genes are correctly identified.
- The experiment will be automated using a Python script to streamline the process of running `gen_analysis.py` for each gene in the list.



## Procedure
1. - Ensure the `Chicago_Ataxia_Exome_Gene_List.tsv` file is available and correctly formatted for input into `gen_analysis.py`.
2. **Prepare the Environment**: Ensure that Python and any necessary libraries (e.g., pandas) are installed on your system.
3. **Load the Gene List**: The `Chicago_Ataxia_Exome_Gene_List.tsv` file will be located in the data/raw folder of the project directory.

4. Run the `gen_analysis.py` script with the `Chicago_Ataxia_Exome_Gene_List.tsv` as input.
```bash
python gen_analysis.py data/raw/Chicago_Ataxia_Exome_Gene_List.tsv
```



### Analysis
- Review the output to determine if `gen_analysis.py` correctly identified all known ataxia-associated genes.



## Investigation of Failure

If the acceptance criteria are not met, the following steps will be taken to investigate the cause of the failure:

1. **Review the Input Data**:
    - Verify that the `Chicago_Ataxia_Exome_Gene_List.tsv` file is correctly formatted and contains all the known ataxia-associated genes.
    - Check for any discrepancies or errors in the gene list that might have affected the results.

2. **Examine the Script**:
    - Inspect the `gen_analysis.py` script for any bugs or issues that might have caused incorrect identification of genes.
    - Ensure that the script is correctly parsing and analyzing the input data.

3. **Check the Environment**:
    - Confirm that all necessary libraries and dependencies are correctly installed and up to date.
    - Ensure that the computational environment is configured correctly and that there are no resource limitations affecting the script's performance.

4. **Analyze the Output**:
    - Review the detailed logs or records of the script's output to identify any patterns or specific genes that were not correctly identified.
    - Compare the output with the expected results to pinpoint where the discrepancies occurred.

### Recommendations

Based on the findings from the investigation, the following recommendations may be made to address the issues:

- **Data Corrections**:
  - Update or correct the `Chicago_Ataxia_Exome_Gene_List.tsv` file to ensure it accurately reflects the known ataxia-associated genes.
  - Implement validation checks to ensure the integrity of the input data before running the analysis.

- **Script Improvements**:
  - Fix any identified bugs or issues in the `gen_analysis.py` script.
  - Enhance the script's error handling and logging capabilities to provide more detailed information in case of failures.

- **Environment Adjustments**:
  - Update or reinstall necessary libraries and dependencies to ensure compatibility with the script.
  - Optimize the computational environment to prevent resource limitations from affecting the script's performance.

- **Re-run the Experiment**:
  - After making the necessary corrections and improvements, re-run the experiment to verify that the acceptance criteria are now met.
  - Document any changes made and ensure that the results are reproducible and meet the 100% accuracy requirement.

## Conclusion
