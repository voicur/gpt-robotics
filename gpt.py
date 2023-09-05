import openai
import multiprocessing
import time

# Function to be run in a process
def commander(api_key, prompt, model, result_dict, proc_name, safety_check=False):
    # Set the API key for this process
    openai.api_key = api_key

    # Send the prompt to the model and get the response
    start_time = time.time()
    response = openai.Completion.create(engine=model, prompt=prompt)
    end_time = time.time()

    # If safety_check is True, use GPT-4 to analyze the code and get a safety score
    if safety_check:
        safety_score = openai.Completion.create(engine='text-davinci-004', prompt='Analyze this code for safety: ' + response.choices[0].text)
        result_dict[proc_name] = (response.choices[0].text, end_time - start_time, safety_score.choices[0].text)
    else:
        result_dict[proc_name] = (response.choices[0].text, end_time - start_time)

if __name__ == "__main__":
    # Create a Manager object to manage shared state
    manager = multiprocessing.Manager()

    # Create a dictionary in server process memory
    result_dict = manager.dict()

    # Create new processes
    process1 = multiprocessing.Process(target=commander, args=('your-gpt-4-key', 'your-prompt', 'text-davinci-004', result_dict, "Process1"))
    process2 = multiprocessing.Process(target=commander, args=('your-gpt-4-key', 'your-prompt', 'text-davinci-004', result_dict, "Process2"))
    process3 = multiprocessing.Process(target=commander, args=('your-gpt-3.5-16k-key', 'your-prompt', 'text-davinci-003.5-16k', result_dict, "Process3", True))

    # Start your processes
    process1.start()
    process2.start()
    process3.start()

    # Join your processes
    process1.join()
    process2.join()
    process3.join()

    # Print results
    for proc_name, result in result_dict.items():
        print(f"{proc_name} completed in {result[1]} seconds with response: {result[0]}")
        if len(result) > 2:
            print(f"Safety score from {proc_name}: {result[2]}")