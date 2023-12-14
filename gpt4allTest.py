import g4f

response = g4f.ChatCompletion.create(
    model=g4f.models.gpt_4,
    messages=[{"role": "user", "content": "So tell me How can I achieve this in Python, replit-code-v1_5-3b-q4_0.gguf search and locate this file that is somewhere located in the directory insde some folder may be inside of other inside folder in the current directory , Provide me only one complete code nothing else with if you need output to you?"}],
) 

print(response)
