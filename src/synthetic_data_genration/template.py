
def SDG_system_message(scenario):
    text='''function call'''
    return f"""
You are an AI assistant specializing in generating synthetic datasets for function calling scenarios. Your task is to create dynamic and context-aware system prompts, tools, and conversations tailored to specific user scenarios. Each scenario will provide a context that you must use to generate:

**Scenario Provided**: {scenario}

1. **Customized System Prompt**: A system message tailored to the scenario, setting the context, role, and specific instructions.
2. **Tools**: Define the tools or functions relevant to the scenario, including their names, descriptions, and parameter structures.Don't use product name as toolname
3. **Conversation**: Simulate a realistic conversation where the user requests a function, and you respond with the appropriate function call and response.
4. **Output Format**: Adhere to the specific #$% format for system_message, tools, and conversation, as outlined below.

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
    system_message:#$% "You are a helpful AI Assistant for function calling, named <Generate random name>. You are speaking with a user named <Random user name>, who lives at <Random address>. The current date and time is <random date and time and time zone (YYYY-MM-DDThh:mm
.sTZD)>. <additional random very generic instructions about  the scenerio>" #$%,        // A more generic system message based on the scenario without user mention user name and product name.
    tools:#$% [
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
    ] #$%,
    conversation:#$% "string" #$%           // A structured conversation based on the scenario, including function calls and responses.Create a lengthly conversation.
}}

"""