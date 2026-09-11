import json
# The json_repair package is one option to pull json from the LLM responses.
# import json_repair
from helper import ask_agent, load_input_data

global function_address
function_address = "" # Global variable to store the function address

def task_1_solution(sample_number: int) -> int:
    """Takes in the static and dynamic analysis data and returns the address
    of the first branch instruction responsible for terminating early and hiding
    the malware's malicious behaviors.
    """
    static_data, api_calls = load_input_data(sample_number)

    static_data, api_calls = load_input_data(sample_number)

    # --- Step 1: Find the 10-call window ---
    
    term_index = -1
    for i, call in enumerate(api_calls):
        # Look for NtTerminateProcess and caller starting with 0x004
        if call['api'] == 'NtTerminateProcess' and call.get('caller', '').startswith('0x004'):
            term_index = i
            break

    if term_index == -1:
        raise ValueError("NtTerminateProcess not found in dynamic API calls.")

    # Get the 10 calls before termination
    start_index = max(0, term_index - 10)
    window = api_calls[start_index:term_index]
    
    # Convert this small list to a JSON string to send to the agent
    api_window_json = json.dumps(window, indent=2)

    # --- Step 2: LLM Call 1 (Find the probe's caller address) ---
    # print(f"API calls window for analysis:\n{api_window_json}\n")

    prompt_1 = f"""
    Here is a list of the 10 API calls that occurred just before process termination:
    {api_window_json}

    Please analyze these 10 calls. Your task is to find the *first* call that is a critical probe that appears before NtTerminateProcess. A critical probe is defined as any of the following(prioritize in this order):
    1. An internet-related API call where 'status' is true and value of 'url' looks like utter nonsense or too long
    2. Probes those related to time or clocks of the system. Ignore GetSystemTimeAsFileTime calls.
    3. A filesystem API call where 'status' is false. Deleting a file is not considered a probe. 
    4. Any other anti-VM or anti-analysis related API calls such as checking for debuggers, registry keys, or system information.

    Return your answer in this EXACT format (two lines only):
    CALLER: <caller address starting with 004, strip out the 0x>
    API: <the exact name of the API function as shown in the json>
    """
    
    response = ask_agent(prompt_1).strip()
    print(f"LLM Response:\n{response}\n")
    
    # Parse the response
    lines = response.split('\n')
    caller_address = None
    api_name = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('CALLER:'):
            caller_address = line.split('CALLER:')[1].strip()
        elif line.startswith('API:'):
            api_name = line.split('API:')[1].strip()
    
    if not caller_address:
        raise ValueError("Could not extract caller address from LLM response")
    if not api_name:
        raise ValueError("Could not extract API name from LLM response")
    
    print(f"Identified caller address: {caller_address}")
    print(f"Identified API: {api_name}")

    # Save entire API call entry to .task1_cache.json
    # Find the entry that matches BOTH the caller address AND the API name
    target_api_entry = None
    full_caller_format = f"0x{caller_address}" if not caller_address.startswith('0x') else caller_address
    
    for call in api_calls:
        caller_match = call.get('caller', '').lower() == full_caller_format.lower()
        api_match = call.get('api', '').lower() == api_name.lower()
        
        if caller_match and api_match:
            target_api_entry = call
            print(f"Found exact match: {call.get('api')} at {call.get('caller')}")
            break
    
    # MUST find exact match 
    if not target_api_entry:
        # Print available entries for debugging
        print(f"\nAvailable API calls in the dataset:")
        for i, call in enumerate(api_calls[:20]):  # Show first 20 for debugging
            print(f"  {i}: caller={call.get('caller')}, api={call.get('api')}")
        raise ValueError(f"Could not find API call entry matching BOTH caller={full_caller_format} AND api={api_name}")
    
    with open(f'sample_{sample_number}/.task1_cache.json', 'w') as f:
        json.dump(target_api_entry, f, indent=2)
    print(f"Saved API call entry: {target_api_entry.get('api')} at {target_api_entry.get('caller')}")

    # --- Step 3: Load 15 lines from static_disassembly.txt starting from the caller address ---
    
    # Read the static disassembly file
    with open(f'sample_{sample_number}/static_disassembly.txt', 'r') as f:
        disassembly_lines = f.readlines()
    
    # Find the line that starts with the caller address
    target_index = -1
    for i, line in enumerate(disassembly_lines):
        if line.strip().startswith(caller_address.upper()):
            target_index = i
            break
    
    if target_index == -1:
        raise ValueError(f"Address {caller_address} not found in static_disassembly.txt")
    
    # Extract 15 lines starting from the target address
    end_index = min(target_index + 15, len(disassembly_lines))
    relevant_disassembly = ''.join(disassembly_lines[target_index:end_index])

    # --- Step 4: LLM Call 2 (Analyze the disassembly to find the first branch instruction) ---

    prompt_2 = f"""
    Here is the disassembly code starting from address {caller_address}:
    
    {relevant_disassembly}
    
    Please analyze this disassembly and identify the first conditional branch instruction (jz or jnz) 
    that could be responsible for early termination of the malware execution.

    Return *only* the address of that branch instruction (must start with "004") and nothing else.
    """
    response = ask_agent(prompt_2)

    branch_address = int(response.strip(), 16)  # Convert hex string to integer
    assert isinstance(branch_address, int), f"The answer must be an integer representing the address, the actual type is: {type(branch_address)}"
    return branch_address



def task_2_solution(sample_number: int) -> str:
    """Takes in the static and dynamic analysis data and returns a Python script
    that sets up the sandbox environment to ensure the malware fully executes.
    """
    static_data, api_calls = load_input_data(sample_number)

    # --- Step 1: Load the cached API call entry from Task 1 ---
    cache_file = f'sample_{sample_number}/.task1_cache.json'
    try:
        with open(cache_file, 'r') as f:
            target_api_call = json.load(f)
            # remove leading '0x' if present and keep 0040xxxx format
            function_address = target_api_call['caller'].removeprefix('0x')
            print(f"Loaded cached API call: {target_api_call['api']} at {target_api_call['caller']}")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid cache file: {e}. Please run task_1_solution first.")
    
    # --- Step 2: Extract 15 lines from static disassembly starting from caller address ---
    with open(f'sample_{sample_number}/static_disassembly.txt', 'r') as f:
        disassembly_lines = f.readlines()
    
    target_index = -1
    search_addr = function_address.upper()
    
    for i, line in enumerate(disassembly_lines):
        if line.strip().startswith(search_addr):
            target_index = i
            break
    
    if target_index == -1:
        raise ValueError(f"Address {function_address} not found in static_disassembly.txt")
    
    # Extract up to 15 lines or until function end (empty line)
    extracted_lines = []
    for i in range(target_index, min(target_index + 15, len(disassembly_lines))):
        line = disassembly_lines[i]
        if line.strip() == '': # Function end
            break
        extracted_lines.append(line)
    
    disassembly_snippet = ''.join(extracted_lines)
    
    # --- Step 3: Generate the bypass script with a single, comprehensive prompt ---
    
    script_prompt = f"""
    Analyze the following malware evasion check and generate a Python 3 script to bypass it.

    **Context:**
    The malware terminates early. The evasion check is centered around the following API call and the subsequent logic.

    **1. API Call Data:**
    {json.dumps(target_api_call, indent=2)}

    **2. Disassembly at Caller Address {function_address}:**
    {disassembly_snippet}

    **Your Task:**
    Generate a complete, self-contained Python 3 script that **changes the sandbox environment state** to bypass this check so the malware's full payload will run.

    Follow these rules for script generation:
    1.  **Analyze the check:**
        * Look at the `api`, `arguments`, and `status` in the API call.
        * Correlate this with the disassembly (e.g., a `cmp` followed by a `jz` or `jnz`).
    2.  **Determine the Bypass Method:**
        * **Filesystem Check:** If the API is checking for a file/directory (e.g., `NtQueryAttributesFile`, `GetFileAttributesA`) and the check *fails* (like `OBJECT_NAME_NOT_FOUND`), the bypass script must **create** that exact file or directory. Use `os.makedirs(path, exist_ok=True)`. The path must be exactly as shown in the `arguments`.
        * **Time Check:** If the API is checking the system time (e.g., `GetSystemTime`) and the disassembly compares the year or time the bypass script must **change the system clock** to that specific year that the malware is looking for, for which you will have to convert the hex value to decimal. Use `os.system()` to run the `date` and `time` commands. Assume the script will be run as an administrator.
        * **Internet Check:** If the API is checking for an internet connection or trying to open a URL that is garbage then do not let it connect. (e.g., `InternetOpenUrlA`, `getaddrinfo`) the bypass script must turn off internet connectivity.
        * **Other Checks:** For other types of checks, deduce the necessary environment change based on the API and disassembly logic.
    3.  **Script Requirements:**
        * The script must use **only standard Python libraries** like `os` and `sys`.
        * **Do not** use `ctypes` or API hooking. This is a system state-change script.
        * The script must be complete, including all necessary imports.
        * For the file creation script, include a check with `os.path.exists()` first.
        * For the time-setting script, include a `try...except` block and print a message that it requires admin rights.

    **Output:**
    Return **ONLY** the complete Python script code, with no other text, markdown, or explanation.
"""
    
    python_script = ask_agent(script_prompt).strip()
    
    # Clean up any markdown formatting
    if python_script.startswith('```'):
        lines = python_script.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        python_script = '\n'.join(lines)
    
    # Write python_script to file for verification
    with open(f'sample_{sample_number}/task2_bypass_script.py', 'w') as f:
        f.write(python_script)
        
    assert isinstance(python_script, str), "The answer must be a python script."
    return python_script