import src.synthetic_data_genration as SDG
import asyncio
from dotenv import load_dotenv

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

sce = """Alice wants to buy a new laptop for her work, focusing on performance, battery life, and portability. She needs a device that can efficiently handle multitasking and various software applications, with a high-resolution display and a comfortable keyboard to match her daily demands."""

# sys = SDG_system_message(sce)
# message = [{"role" : "system", "content" : sys}]
# response = asyncio.run(LLM_model.text_completion(message))
# total_tokens = response.usage.total_tokens

#addition instrution is more detailed
#tools also more based on scenerio
#conversation need to be more enhanced




def process_the_document(document):
    # for scenerio in document["scenerio"]:
        sys = SDG_system_message(document)
        message = [{"role" : "system", "content" : sys}]
        response = asyncio.run(LLM_model.text_completion(message))
        result=response.choices[0].message.content
        extracted_content = extract_json_content(result)
        if extracted_content:
            print(json.dumps(extracted_content, indent=2))

        data = extracted_content
        res=data[0]
        print(res)
        print(type(res))
        # data = json.loads(res)

        # # Output the extracted variables
        # print("System Message:", system_message)
        # print("Tools:", tools)
        # print("Conversation:", conversation)
        total_tokens = response.usage.total_tokens
        
# print(process_the_document('.scenario.xlsx'))
print(process_the_document(sce))