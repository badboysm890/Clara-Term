import re
import subprocess
import time
import logging
from langchain.chat_models import ChatOpenAI
import os
import time
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import g4f
import ollama
import platform
import getpass

g4f.debug.logging = True  # Enable debug logging
g4f.debug.check_version = False  # Disable automatic version checking

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
verbose_logging = os.getenv('VERBOSE', 'False') == 'True'

logging.basicConfig(level=logging.DEBUG, filename='run.log', filemode='w')
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

script_filename = ""
MODEL_TYPE = "llama3"

class FolderNameGenerator:
    def __init__(self):
        self.llm = OpenAI(temperature=0.9, openai_api_key=openai_api_key)
        self.prompt = PromptTemplate(
            input_variables=["query"],
            template="The Query is ' {query} ', Provide me a title in the format --<Title here>--. Only the folder name and not path or anything else. Note: Give me a 10-15 character folder name."
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_unique_foldername(self, query):
        logging.info("Generating unique folder name...")
        folder_name = self.chain.run({"query": query})
        logging.debug(f"LLM Response for folder name: {folder_name}")
    
        print("foldername", folder_name)

        match = re.search(r'--(.*?)--', folder_name)
        print("match", match)

        if match:
            folder_name = match.group(1).strip()
            timestamp = str(int(time.time()))
            return f"{folder_name}{timestamp}"
        else:
            timestamp = str(int(time.time()))
            return f"{query.replace(' ', '_')}{timestamp}"

class OtherFilesGenerator:
    def __init__(self, api_key, is_offline=False):
        self.is_offline = is_offline
        if not is_offline:
            self.llm = ChatOpenAI(openai_api_key=api_key)

        
    def predict(self, prompt):
        if self.is_offline:
            # Using g4f for predictions when offline
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
                provider=g4f.Provider.Bing,
            )
            # Directly return the response string
            return response
        else:
            # return self.llm.predict(prompt)
            logging.info("Predicting using Ollama...")

            response = ollama.generate(model=MODEL_TYPE, 
            prompt=prompt,
            )
            return response['response']
        
    def generate_other_files(self, code):
        logging.info("Checking if other files are required... for running the code")
        data =  self.predict(code+"' this is the code i wrote but its not running becoz it needs some other files, what other files are required to run this code? please provide the Code, FileName and Extension of the file. Provide the code")
        # print("data", data)
        return data
    
class DynamicAgent:
    
    def __init__(self, api_key, is_offline=False):
        self.is_offline = is_offline
        self.execution_count = 0
        self.query = ""
        if not is_offline:
            self.llm = ChatOpenAI(openai_api_key=api_key)
        logging.info("DynamicAgent initialized.")

    def predict(self, prompt):
        if self.is_offline:
            # Using g4f for predictions when offline
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
                provider=g4f.Provider.Bing,
            )
            # Directly return the response string
            return response
        else:
            # return self.llm.predict(prompt)
            logging.info("Predicting using Ollama...")
            response = ollama.generate(model=MODEL_TYPE, 
            prompt=prompt,
            )
            return response['response']

    def generate_unique_foldername(self, query):
       logging.info("Generating unique folder name...")
       folder_name_generator = FolderNameGenerator()
       return folder_name_generator.generate_unique_foldername(query)
    
    def generate_unique_filename(self):
        # use LLM to generate a unique filename by providing the q
        timestamp = str(int(time.time()))
        return f"temp_script_{timestamp}.py"

    def generate_other_files(self, code):
        # use the OtherFilesGenerator  to generate other files
        other_files_generator = OtherFilesGenerator(None, is_offline=self.is_offline)
        return other_files_generator.generate_other_files(code)
    
    def create_files_from_string(self,input_string, folder_path):
        code_blocks = re.findall(r'```([a-zA-Z]+)\n(.*?)```', input_string, re.DOTALL)
        file_name_pattern = r'<title>(.*?)<\/title>'
        try:
            for extension, code in code_blocks:
                # Extract file name if available
                file_name_match = re.search(file_name_pattern, code)
                if file_name_match:
                    file_name = file_name_match.group(1)
                else:
                    file_name = "unnamed"
                
                # Create folder if it doesn't exist
                full_folder_path = os.path.join(folder_path, extension)
                if not os.path.exists(full_folder_path):
                    os.makedirs(full_folder_path)
                
                # Create file and write code to it
                with open(f"{full_folder_path}/{file_name}.{extension}", 'w') as f:
                    f.write(code)
        except Exception as e:
            print("Error in create_files_from_string", e)
            return "Error in create_files_from_string"
    
    def determine_task(self, query):
        logging.info("Determining task from the provided query...")
        # Replace self.llm.predict with self.predict
        logging.debug(f"Query: {query}")
        os_name = platform.system()
        os_version = platform.release()
        
    
        # Get system username
        username = getpass.getuser()
        return self.predict(f"""Note: You are an interactive terminal who does the job using Python code. The current OS is {os_name} {os_version}, and the system username is {username}.
 , So tell me How can I achieve this in Python {query} and give code only inside it in this format with codeblock -> ```    ``` (function used to extract the code re.search(r'```(?:Python|python)?\n(.*?)```', full_code, re.DOTALL)) open and close should be there at any cost but only once, you must provide me only one complete code block and nothing else and please don't provide any other information except the code.""")

    def extract_executable_code(self, full_code):
        logging.info("Extracting code segment...")
        # code format
        '''
        ```Python
        import psutil
        import time

        while True:
            battery = psutil.sensors_battery()
            print(f"Current Battery Level: {battery.percent}%", end='\r')
            if not battery.power_plugged:
                print("Not Plugged In")
            else:
                print("Plugged In")
            time.sleep(1)
        ```
        '''
        extracted_code = re.search(r'```(?:Python|python)?\n(.*?)```', full_code, re.DOTALL)
        
        if extracted_code:
            logging.debug(f"Extracted code: {extracted_code.group(1).strip()}")
            return extracted_code.group(1).strip()
        else:
            logging.error("Failed to extract code.")
            code = self.predict(full_code+" in the above code or text just extract the code alone in this format ```<code>```")
            print(code)
            extracted_code = re.search(r'```(?:Python|python)?\n(.*?)```', code, re.DOTALL)
            if extracted_code:
                logging.debug(f"Extracted code: {extracted_code.group(1).strip()}")
                return extracted_code.group(1).strip()
        
        # return "print('Code Extraction failed follow this format ```<code>```')"

    def validate_extracted_code(self, code):
        logging.info("Validating the extracted code...")
        logging.debug(f"Validating code: {code}")
        return bool(self.extract_executable_code(code))

    def fetch_and_validate_solution(self, query):
        logging.info("Fetching and validating solution...")
        full_solution = self.determine_task(query)
        logging.debug(f"Full solution: {full_solution}")
        # if self.validate_extracted_code(full_solution):
        #     return full_solution
        # else:
        return self.extract_executable_code(full_solution)

    def detect_dependencies(self, code):
        logging.info("Detecting dependencies required for the generated code...")
        logging.debug(f"Code to detect dependencies: {code}")
        detected_imports_response = self.predict(f"Check the import statements in the given code and give all necessary pip installables if no package needed or if its inbuild then skip else provide as copy-paste snippet? {code}")
        dependencies = re.findall(r'pip install ([\w\-]+)', detected_imports_response)
        logging.debug(f"Detected dependencies: {dependencies}")
        return dependencies

    def ensure_dependencies_installed(self, dependencies):
        logging.info("Ensuring all detected dependencies are installed...")
        for package in dependencies:
            try:
                logging.debug(f"Installing {package}...")
                subprocess.check_output(['pip', 'install', package])
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install {package}")
                logging.error(e)
                return f"Failed to install {package}"
        return "Dependencies installed successfully."

    def execute_code(self, code, other_files):
        logging.info("Executing the generated code...")
        logging.debug(f"Code to execute: {code}")
        executable_code = self.extract_executable_code(code)
        logging.debug(f"Executable code: {executable_code}")

        if not executable_code:
            return "Error: Code extraction failed.", None, None
    
        # Display the code to the user for review and ask for confirmation
        print("Generated code to execute:\n")
        print(executable_code)
        execute_confirmation = input("Do you want to execute this code? (y/N): ")
        if execute_confirmation.lower() != 'y':
            return "Execution aborted by the user.", None, None
    
        script_filename = self.generate_unique_filename()
    
        with open(script_filename, 'w') as f:
            f.write(executable_code)
    
        # Create other files
        self.create_files_from_string(other_files, ".")
    
        try: 
            output = subprocess.run(['python', script_filename], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output.stdout.decode('utf-8').strip(), None, script_filename
        except subprocess.CalledProcessError as e:
            print("----------------ERROR----------------")
            error_message = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
            with open(script_filename, 'r') as file:
                executable_code = file.read()
            return f"Error during execution: {error_message}", executable_code, script_filename
    
    def fix_and_execute_code(self, error, code):
        # for _ in range(5):

        logging.info("Attempting to fix the code...")
        logging.debug(f"Error: {error}\n")
        logging.debug(f"Failed Code: {code}\n")
        fix_instruction = self.predict(f"fix this error: '{error}' in the following code: ```{code}``` and Provide the correct complete code")
        if self.execution_count > 2:
            print("-----------------Trying Different Approach-----------------")
            fix_instruction = self.predict(f"the following code ```{code}``` generated an error: '{error}', can you try different approach to solve the query?{self.query}")
            logging.debug(f"Trying different approach to solve the error: {fix_instruction}")
        try:
            dependencies = self.detect_dependencies(fix_instruction)
            self.ensure_dependencies_installed(dependencies)
        except:
            logging.info("Meh i couldn't handle deps.")
        fixed_code = self.extract_executable_code(fix_instruction)

        # if not fixed_code:
        #     continue
        
        try:
            script_filename = self.generate_unique_filename()
            with open(script_filename, 'w') as f:
                f.write(fixed_code)
        except:
            logging.info("Meh i couldn't handle save")
        
        other_files = self.generate_other_files(fixed_code)
        result, failed_code, script_filename = self.execute_code(fixed_code, other_files)
        print("Result--->", result)
        if failed_code:
            print("---------------Retrying----------------")
            result = self.fix_and_execute_code(result, failed_code)
        return result
        # self.prompt_delete_files(script_filename)

        # try:
        #     output = subprocess.check_output(['python', script_filename])
        #     return output.decode('utf-8').strip()
        # except subprocess.CalledProcessError as e:
        #     error = e.output.decode('utf-8').strip()
        #     with open(os.path.join("temp", "final_attempted_code.py"), 'w') as f:
        #         f.write(fixed_code)
        # return f"Error during re-execution after fixing: {error}"
        
    def prompt_delete_files(self, folder_path):
       response = input("Would you like to delete the created files? (y/N): ")
       if response.lower() == 'y':
        #    delete the file using
           os.remove(folder_path)
           print("Files deleted.")
       else:
           print("Files kept.")
        
    def process_query(self, query):
        self.query = query
        logging.info("Processing the user query...")
        code_to_run = self.fetch_and_validate_solution(query)
        other_files = self.generate_other_files(code_to_run)
        detected_dependencies = self.detect_dependencies(code_to_run)
        dependencies_status = self.ensure_dependencies_installed(detected_dependencies)
        if "failed" in dependencies_status.lower():
            print(dependencies_status)
        result, failed_code, script_filename = self.execute_code(code_to_run, other_files)

        print("Result--->", result)
        
        if failed_code:
            print("---------------Retrying----------------")
            result = self.fix_and_execute_code(result, failed_code)
        self.prompt_delete_files(script_filename)
        
        return result