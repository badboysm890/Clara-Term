import os
import redis
import argparse
from dotenv import load_dotenv
from ClaraKernel import DynamicAgent

# Load environment variables
load_dotenv()

def main(args):
    query = args.input
    agent = DynamicAgent(os.getenv('OPENAI_ACCESS_KEY'))
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