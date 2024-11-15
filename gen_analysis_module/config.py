from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from loguru import logger
import os



# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

ENV_FILE_PATH = PROJ_ROOT / "gen_analysis.env"

load_dotenv(find_dotenv(ENV_FILE_PATH))
PROMPTS_JSON_PATH = PROJ_ROOT / os.environ.get("prompts_json_file")



# add test directory and test data locations
TEST_DIR = PROJ_ROOT / "tests"
TEST_DATA_DIR = TEST_DIR / "data"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
