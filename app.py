import src.synthetic_data_genration as SDG
import asyncio
from dotenv import load_dotenv

load_dotenv()

LLM_model = SDG.LlmModel.from_config("together_ai", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", 0, 4096)
#LLM_model = SDG.LlmModel.from_config("aimlapi", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", 0, 4096)


def SDG_system_message(scenario):
    return f"""
You are an AI assistant specializing in generating synthetic datasets for function calling scenarios. Your task is to create dynamic and context-aware system prompts, tools, and conversations tailored to specific user scenarios. Each scenario will provide a context that you must use to generate:

**Scenario Provided**: {scenario}

1. **Customized System Prompt**: A system message tailored to the scenario, setting the context, role, and specific instructions.
2. **Tools**: Define the tools or functions relevant to the scenario, including their names, descriptions, and parameter structures.
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
      ASSISTANT: <functioncall> {{json function call}}
      ```
    - Function call responses must be formatted as:
      ```
      FUNCTION RESPONSE: {{json function response}}
      ```

 - Scenario Customization:
    - Use the scenario details to adjust the system message, ensuring it reflects the specific context or use case.
    - Define tools that are directly relevant to the scenario, adjusting their descriptions and parameters accordingly.
    - Generate a conversation that accurately represents a user interacting with the defined tools within the scenario's context.

You should use the following JSON format for output format:

output_format: {{
    system_message: "You are a helpful AI Assistant for function calling, named <Generate random name>. You are speaking with a user named <Random user name>, who lives at <Random address>. The current date and time is <random date and time and time zone (YYYY-MM-DDThh:mm
.sTZD)>. <addtinal random instructions about main intent of scenerio>",        // A customized system message based on the scenario.
    tools: [
        {{
            "name": "ToolName",
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
    conversation: "string"           // A structured conversation based on the scenario, including function calls and responses.
}}
"""

sce = """Alice wants to buy a new laptop for her work, focusing on performance, battery life, and portability. She needs a device that can efficiently handle multitasking and various software applications, with a high-resolution display and a comfortable keyboard to match her daily demands."""

sys = SDG_system_message(sce)
message = [{"role" : "system", "content" : sys}]
response = asyncio.run(LLM_model.text_completion(message))
print(response.choices[0].message.content)

#addition instrution is more detailed
#tools also more based on scenerio
#conversation need to be more enhanced
