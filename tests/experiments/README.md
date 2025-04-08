# Experiment: Evaluating Gene Implication in Ataxia Using `gen_analysis`

## Background

This experiment investigates the feasibility of using OpenAI’s GPT-4 API to classify whether genes are associated with ataxia, a neurological disorder. The gene list used is from the curated `Chicago_Ataxia_Exome_Gene_List_2.tsv`, which contains genes already known to be implicated in ataxia. The goal is to test the classification accuracy of a natural language model on biomedical data, without explicitly training it on domain-specific sources.

## Summary

The experiment uses a script (`ataxia_api_test.py`) to query GPT-4 for each gene symbol in the list and asks if it is associated with ataxia. The response is categorized as:

- **1** = Yes (associated)
- **0** = No (not associated)
- **2** = Uncertain

Another script (`ataxia_api_analysis.py`) analyzes the output and computes summary statistics and a chi-square test to measure deviation from expected classification.

## Purpose

To determine if the GPT-4 model can correctly identify all known ataxia-associated genes based solely on symbolic prompts. Since the input gene list is curated for ataxia, the expected result is a 97.2% positive classification and 2.8% negative classifications.

## Scope

### Acceptance Criteria

- The script must flag **97.2%** of the genes as associated with ataxia (i.e., API_Flag = 1 for all entries).
- The script must flag **2.8%** of the genes as not associated with ataxia (i.e., API_Flag = 0 for all entries).
- The results must be reproducible under the same conditions.
- Deviations (false negatives or uncertain classifications) will constitute a failed experiment.
- Logs and outputs must be collected for auditing and verification.

## Materials

- `Chicago_Ataxia_Exome_Gene_List.tsv_2` (723 known ataxia genes)
- Scripts: `ataxia_api_test.py`, `ataxia_api_analysis.py`
- Azure OpenAI GPT-4 API access
- Python environment with dependencies (pandas, openai, scipy, etc.)

## Methodology

- Each gene symbol is sent to GPT-4 with a standard prompt asking whether it is associated with ataxia.
- The model’s response is categorized and saved.
- The output is statistically analyzed for precision and consistency using chi-square tests.
- Classifications are compared against the expectation that all genes are truly associated.

## Procedure

1. Confirm that the gene list exists and is in the correct format.
2. Configure the environment using `gen_analysis.env` to authenticate OpenAI API access.
3. Run the following command to initiate gene classification:

    ```bash
    python ataxia_api_test.py
    ```

4. Analyze the results:

    ```bash
    python ataxia_api_analysis.py
    ```

## Analysis

From 703 genes tested:

- **Correctly flagged (TP)**: 628 (86.86%)
- **Incorrectly flagged as not associated (FN)**: 94 (13.00%)
- **Uncertain classifications**: 1 (0.14%)

Chi-square test:

- **Statistic**: 53.26123347436962
- **p-value**: 2.719381266129593e-12
- **Degrees of freedom**: 2

## Investigation of Failure

### Why the Experiment Failed

Despite its strengths, GPT-4 is a general-purpose model that wasn't explicitly trained on structured biomedical association data. Several factors contributed to the failure:

- The model lacks consistent domain knowledge from curated biomedical databases.
- Responses are probabilistic and sensitive to prompt wording.
- The model is conservative when unsure, often defaulting to “Uncertain.”
- Simple prompts may not provide the necessary structure to extract reliable answers.

### Diagnostic Steps

1. **Input Validation**: The gene list is accurate and complete.
2. **Code Review**: The scripts correctly parsed inputs and formatted queries.
3. **Output Examination**: Many uncertain results occurred for well-known genes.
4. **Statistical Check**: Chi-square analysis confirmed significant deviation from expectation.

## Recommendations

- **Improve Prompts**: Use more structured and specific language referencing known sources (e.g., “Is this gene associated with ataxia according to OMIM?”).
- **Use Domain Models**: Consider switching to biomedical-specific models like BioGPT or PubMedBERT.
- **Add Fallbacks**: For “Uncertain” cases, implement a manual review or a second-tier query.
- **Validate Data**: Perform more preprocessing or augmentation to help steer the model.
- **Retrain with Feedback**: Consider fine-tuning a smaller model with labeled examples.

## Conclusion
This experiment evaluated GPT-4's ability to classify genes as associated with ataxia using only gene symbols and natural language prompts. Although the model demonstrated some capacity to identify known associations—correctly flagging 86.86% of the genes—its performance fell short of the expected 97.2% accuracy, with 13.00% false negatives and a small fraction (0.14%) marked as uncertain. The statistical analysis confirmed a significant deviation from expected results, indicating that GPT-4, in its current general-purpose configuration, is not sufficiently reliable for high-precision biomedical classification tasks.

The failure highlights limitations in GPT-4’s domain-specific recall, particularly in cases requiring structured biological knowledge. The model's conservative tendencies and reliance on prompt interpretation contribute to inconsistent outputs. To improve future results, we recommend refining prompts, incorporating biomedical-tuned models, and using fallback strategies for ambiguous classifications. Ultimately, while GPT-4 offers a promising tool for exploratory queries, it currently lacks the precision and consistency required for authoritative gene-disease association analysis without domain adaptation or structured guidance.