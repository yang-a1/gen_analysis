from pathlib import Path
import json
from dotenv import load_dotenv, find_dotenv
from loguru import logger
import os
import re



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

PROJ_ROOT = Path(__file__).parent.parent
prompts_json_filename = os.environ.get("prompts_json_file")

# Use None or default to an empty path if the environment variable is not set
PROMPTS_JSON_PATH = PROJ_ROOT / prompts_json_filename if prompts_json_filename else None

VARIANT_DESCRIPTION_PATH = os.path.join(PROJ_ROOT, "variant_description.json")

MAX_TOKENS_VALUE = int(os.environ.get('max_tokens', 0))
TEMPERATURE_VALUE = float(os.environ.get('temperature', 0.0))

if MAX_TOKENS_VALUE  > 1000:
    print(f"Max tokens in the env file is {MAX_TOKENS_VALUE}.")
    user_confirmation = input(f"The max_tokens value is greater than 1000. Do you want to proceed? (yes/no): ")
    if user_confirmation.lower() != 'yes':
        raise ValueError("Operation aborted by the user due to max_tokens exceeding 1000.")



# Read the CSS file
CSS_PATH = PROJ_ROOT / 'gen_analysis.css'





def prompts_color_configuration(prompts_json_path, CSS_PATH, replacement_string="reassign_me_"):
    """
    Loads prompts from a JSON file.  Check if any prompt keys are in the CSS file.
    If not, then add the key to the CSS file as one of the replacement_string values.
    This function assumes that all prompt keys are h2 headers in the CSS file.
    Args:
        prompts_json_path (str): The path to the JSON file containing prompts.
        CSS_CONTENT (str): The content of the CSS file.
        replacement_string (str): The string to be replaced in the CSS content. Default is "reassign_me".
    Returns:
        dict: A dictionary containing the prompts.
    Example:
        prompts = load_prompts('prompts.json')
    """
    with open(prompts_json_path, 'r') as file:
        prompts = json.load(file)

    # create a list of keys from the prompts dictionary and add "h2." to each key
    keys = prompts.keys()

    with open(CSS_PATH, 'r') as css_file:
        CSS_CONTENT = css_file.read()

    # get all the words in the CSS_CONTENT file that have the replacement_string in them
    words = re.findall(r'\b' + re.escape(replacement_string) + r'\w+', CSS_CONTENT)

    # check to see if the key is in the CSS_CONTENT file.  If it is not, then add the key to the CSS_CONTENT file by replacing the first word that has the replacement_string with the key
    for key in keys:
        if key not in CSS_CONTENT:
            # replace word[0] with the key and then remove word[0] from the list of words
            CSS_CONTENT = re.sub(r'\b' + re.escape(replacement_string) + r'\w+', key, CSS_CONTENT, 1)
            words.remove(words[0])

    with open(CSS_PATH, 'w') as css_file:
        css_file.write(CSS_CONTENT)
    return CSS_CONTENT


try:
    CSS_CONTENT = prompts_color_configuration(PROMPTS_JSON_PATH, CSS_PATH)
except Exception as e:
    logger.error(f"Failed to configure prompts color: {e}")

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
