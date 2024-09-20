#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = gen_analysis
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	conda env update --name $(PROJECT_NAME) --file environment.yml --prune




## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 gen_analysis_module
	isort --check --diff --profile black gen_analysis_module
	black --check --config pyproject.toml gen_analysis_module

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml gen_analysis_module




## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	conda env create --name $(PROJECT_NAME) -f environment.yml

	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make Dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) gen_analysis_module/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)


## Checks for updates and reloads gen_analysis module if there are changes. Runs pytest
.PHONY: test
test: requirements
	bash -c "source ~/.bashrc && conda activate $(PROJECT_NAME) && pytest"

## Run SLURM job to execute working_openAI_test.py
## add requirements to slurm_test
.PHONY: slurm_test
slurm_test: requirements
	bash tests/slurm/slurm_request_run_working_openAI_test.sh

## run test using slurm with sbatch command
.PHONY: sbatch_test
sbatch_test: requirements
	sbatch --time=10:00 --cpus-per-task=1 --wrap="bash -c 'source ~/.bashrc && conda activate $(PROJECT_NAME) && pytest'" | tee temp_slurm_job_id.txt
	sleep 10
	@job_id=$$(cat temp_slurm_job_id.txt | awk '{print $$4}'); \
	echo "Waiting for job $$job_id to complete..."; \
	sacct -j $$job_id --format=State --noheader | grep -q "COMPLETED" || sleep 1; \
	while ! sacct -j $$job_id --format=State --noheader | grep -q "COMPLETED"; do sleep 1; done; \
	echo "Job $$job_id completed. Output:"; \
	cat slurm-$$job_id.out; \
	rm temp_slurm_job_id.txt; \
	rm slurm-$$job_id.out




## Run all test functions
.PHONY: test_all
test_all: test slurm_test sbatch_test