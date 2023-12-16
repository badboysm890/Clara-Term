import os
import argparse
from .ClaraKernel import DynamicAgent
from dotenv import load_dotenv, set_key

# Define the path to the .env file
dotenv_path = '.env'

# Load existing environment variables
load_dotenv(dotenv_path)

def set_offline_mode():
    """Set the offline mode in the .env file."""
    set_key(dotenv_path, "OFFLINE_MODE", "true")
    load_dotenv(dotenv_path)

def get_openai_access_key():
    """Get the OPENAI_ACCESS_KEY from environment or prompt the user."""
    key = os.getenv('OPENAI_API_KEY')
    offline = os.getenv('OFFLINE_MODE')
    if key is None and offline is None:
        response = input("OpenAI API key not found. Do you want to switch to free models ?  Or Choose No to use OpenAI (Recommended)? (Y/N): ")
        if response.lower() in ['y', 'yes']:
            set_offline_mode()
            return None
        else:
            key = input("Enter your OpenAI Access Key: ")
            # Save the key in .env file
            set_key(dotenv_path, "OPENAI_API_KEY", key)
            load_dotenv(dotenv_path)  # Reload the .env file
    return key

def main(args):
    access_key = get_openai_access_key()
    is_offline = os.getenv('OFFLINE_MODE') == 'true'
    query = args.input
    agent = DynamicAgent(access_key, is_offline=is_offline)
    response = agent.process_query(query)
    print(response)

def cli():
    parser = argparse.ArgumentParser(description='My Command Line Interface (CLI) app')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input for the command')

    args = parser.parse_args()
    main(args)

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print(e)
        print("Unexpected error occurred, stopping the program.")
