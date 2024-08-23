import src.synthetic_data_genration as SDG
import asyncio, os, uuid, json, re
from dotenv import load_dotenv
import pandas as pd
from tqdm.asyncio import tqdm
load_dotenv()

mongo_db = SDG.mongo_db(os.getenv("cosmosdb_connection_string"), "incle")

conversation_pattern = r'conversation:#\$%\s*([\s\S]*?)\s*#\$%'
tools_pattern = r'tools:#\$%\s*\[\s*([\s\S]*?)\s*\]\s*#\$%'
system_message_pattern = r'system_message:#\$%\s*"([\s\S]*?)"\s*#\$%'


async def process_the_document(user_id, document_id, mail_id ,document, client, model, file_output_format):
    token_use = 0
    LLM_model = SDG.LlmModel.from_config(client, model, 0, 4096)
    for scenario in tqdm(document["scenerio"], desc="Processing Scenarios"):
        try:
            retries = 3  
            while retries > 0:
                system_message_content = None
                tools_content = None
                conversation_content = None

                sys = SDG.SDG_system_message(scenario)
                message = [{"role": "system", "content": sys}]
                response = await LLM_model.text_completion(message)
                if response.choices:
                    result = response.choices[0].message.content
                    system_message_match = re.search(system_message_pattern, result, re.DOTALL)
                    tools_match = re.search(tools_pattern, result, re.DOTALL)
                    conversation_match = re.search(conversation_pattern, result, re.DOTALL)

                    if system_message_match:
                        system_message_content = system_message_match.group(1)
                    if tools_match:
                        tools_content = tools_match.group(1)
                    if conversation_match:
                        conversation_content = conversation_match.group(1)

                    if system_message_content and tools_content and conversation_content:
                        total_tokens = response.usage.total_tokens
                        token_use += total_tokens

                        payload = {
                            "user_id": user_id,
                            "document_id": document_id,
                            "mail_id" : mail_id,
                            'scenario': scenario,
                            'system_message': system_message_content,
                            'tools': tools_content,
                            'conversation': conversation_content,
                            'model': model,
                            'total_tokens': total_tokens
                        }
                        mongo_db.insert_one("SDG_synthetic_data", payload)
                        break 
                    else:
                        retries -= 1  
                        print(f"Incomplete data, retrying... {retries} attempts left for the user id {user_id}")
                else:
                    print(f"No response for scenario: {scenario}")
                    retries -= 1
            if client in ["together_ai", "groq"]:
                await LLM_model.rotate_client(client)

        except Exception as e:
            if '429' in str(e):
                print("Rate limit hit, rotating client or switching API...")
                if client == "together_ai":
                    await LLM_model.rotate_client('together_ai')
                elif client == "groq":
                    await LLM_model.rotate_client('groq')
                else:
                   
                    client = "groq"
                    model = "llama-3.1-70b-versatile"
                    LLM_model = SDG.LlmModel.from_config(client, model, 0, 4096)
            else:
                print("Error during completion:", str(e))
                retries -= 1 
        
    return {
        "user_id": user_id,
        "document_id": document_id,
        "output_format": file_output_format,
        "tokens_used": token_use
    }
