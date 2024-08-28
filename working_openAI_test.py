

from openai import AzureOpenAI
import os
from dotenv import load_dotenv

print("starting test")

# env_path = Path("20240314_gpt.env").resolve()
#Sets the current working directory to be the same as the file.
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

# print cwd
print(os.getcwd())
print("loading .env file")

env_file_path = "/nfs/turbo/umms-mblabns/test/20240809_gpt.env"



#Load environment file for secrets.
try:

    if load_dotenv(env_file_path) is False:
        raise TypeError
except TypeError:
    print('Unable to load .env file.')
    quit()

print("creating client")
#Create Azure client
client = AzureOpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
    api_version=os.environ['API_VERSION'],
    azure_endpoint = os.environ['openai_api_base'],
    organization = os.environ['OPENAI_organization']
)

# Send a completion call to generate an answer
print('Sending a test completion job')

response = client.chat.completions.create(
        # model=os.environ['model'],
        # model="gpt-3.5-turbo", # this doesn't work
        # model="gpt-4", # this works
        # model="gpt-35-turbo", # this works
        model=os.environ['model'],
        messages=[
            {"role": "system", "content": "Answer the question as a pirate."},
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        temperature=0,
        stop=None)

#Print response.
print(response.choices[0].message.content)

