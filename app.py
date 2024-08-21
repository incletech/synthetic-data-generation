import src.synthetic_data_genration as SDG
import asyncio, os
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm
load_dotenv()


import json
import re

def extract_json_content(text, marker="```"):
    pattern = re.compile(rf'{re.escape(marker)}(.*?){re.escape(marker)}', re.DOTALL)
    matches = pattern.findall(text)
    
    # Return the matches
    return matches


LLM_model = SDG.LlmModel.from_config("together_ai", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", 0, 4096)
#LLM_model = SDG.LlmModel.from_config("aimlapi", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", 0, 4096)


def SDG_system_message(scenario):
    text='''function call'''
    return f"""
You are an AI assistant specializing in generating synthetic datasets for function calling scenarios. Your task is to create dynamic and context-aware system prompts, tools, and conversations tailored to specific user scenarios. Each scenario will provide a context that you must use to generate:

**Scenario Provided**: {scenario}

1. **Customized System Prompt**: A system message tailored to the scenario, setting the context, role, and specific instructions.
2. **Tools**: Define the tools or functions relevant to the scenario, including their names, descriptions, and parameter structures.Don't use product name as toolname
3. **Conversation**: Simulate a realistic conversation where the user requests a function, and you respond with the appropriate function call and response.

Rules:
- **Conversation Format**:
    - Use the following format:
      ```
      USER: [user message]
      ASSISTANT: [assistant message]
      ```
    - Function call invocations must be formatted as:
      ```
      ASSISTANT: {text} {{json function call}} 
      ```
    - Function call responses must be formatted as:
      ```
      FUNCTION RESPONSE: {{json function response}}
      ```
      ASSISTANT: give the FUNCTION RESPONSE in user friendly formatted
      ```

 - Scenario Customization:
    - Use the scenario details to adjust the system message, ensuring it reflects the specific context or use case.
    - Define tools that are directly relevant to the scenario, adjusting their descriptions and parameters accordingly.
    - Generate a conversation that accurately represents a user interacting with the defined tools within the scenario's context.

You should use the following JSON format for output format:

output_format: {{
    system_message: "You are a helpful AI Assistant for function calling, named <Generate random name>. You are speaking with a user named <Random user name>, who lives at <Random address>. The current date and time is <random date and time and time zone (YYYY-MM-DDThh:mm
.sTZD)>. <additional random very generic instructions about  the scenerio>",        // A more generic system message based on the scenario without user mention user name and product name.
    tools: [
        {{
            "name": "ToolName", // Don't use the product name as ToolName
            "description": "Describes what the tool does and its purpose.",.
            "parameters": {{ 
                "properties": {{ 
                    "paramName": {{
                        "type": "String|Number|Boolean|Object|Array|Enum",
                        "description": "Detailed description of the parameter.",
                        "enum": "Optional array, if applicable"
                    }},                                     // each entry should be a separate JSON object within the array.
                }},
                "required": ["List of required parameters"]  
            }}
        }},       // each tool should be a separate JSON object within the array.
    ],
    conversation: "string"           // A structured conversation based on the scenario, including function calls and responses.Create a lengthly conversation.
}}

"""
# Regex pattern to capture each section
system_message_pattern = r'"system_message": "(.*?)"(?=,)'
tools_pattern = r'"tools": \[(.*?)](?=,)'
conversation_pattern = r'"conversation":\s*("\s*(?:[^"\\]*(?:\\.[^"\\]*)*)\s*")(?=\s*,|\s*\})'
 

async def process_the_document(user_id, document, file_output_format):
    columns = ['Scenario', 'System Message', 'Tools', 'Conversation', 'Total Tokens']
    rows = []
    output_dir = f"./output/"
    os.makedirs(output_dir, exist_ok=True)
    for scenario in tqdm(document["scenerio"], desc="Processing Scenarios"):
        try:
            sys = SDG_system_message(scenario)
            message = [{"role" : "system", "content" : sys}]
            response = await LLM_model.text_completion(message)
            if response.choices: 
                result = response.choices[0].message.content
                print(result)
                system_message = re.search(system_message_pattern, result, re.DOTALL)
                print(system_message)
                tools = re.search(tools_pattern, result, re.DOTALL)
                print(tools)
                conversation = re.search(conversation_pattern, result, re.DOTALL)
                print(conversation)
                total_tokens = response.usage.total_tokens
                print(total_tokens)

                rows.append({
                    'Scenario': scenario,
                    'System Message': system_message.group(1) if system_message else None,
                    'Tools': tools.group(1) if tools else None,
                    'Conversation': conversation.group(1) if conversation else None,
                    'Total Tokens': total_tokens
                })
            else:
                print(f"No response for scenario: {scenario}")
            await LLM_model.rotate_client('together_ai')

        except Exception as e:
            print("Error during completion:", str(e))
            await LLM_model.rotate_client('together_ai') 
            continue 

    data = pd.DataFrame(rows, columns=columns)
    file_path = f"{output_dir}report_{user_id}.{file_output_format.lower()}"

    if file_output_format.lower() == "csv":
        data.to_csv(file_path, index=False)
    elif file_output_format.lower() == "excel":
        data.to_excel(file_path, index=False)
    else:
        raise ValueError("File output format is not supported")

    return f"File is processed successfully and stored at {file_path}"


import asyncio
data=pd.read_excel("C:\\Users\\Gokul\\Desktop\\Hackthon\\synthetic-data-generation\\scenario.xlsx")
print(data)
x = asyncio.run(process_the_document("24524524",data, "csv"))
print(x)
