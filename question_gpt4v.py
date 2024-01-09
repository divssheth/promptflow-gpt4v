from promptflow import tool
from promptflow.connections import CustomConnection, AzureOpenAIConnection
import json
import requests
import traceback
import time

system_message = """
First describe the video in detail paying close attention to Product characteristics highlighted, 
    Background images, Lighting, Color Palette and Human characteristics for persons in the video. 
    Explicitly mention the product brand or logo. Finally provide a summary of the video 
    and talk about the main message the advertisement video tries to convey to the viewer.
"""
def call_gpt4v(GPT_4V_ENDPOINT, GPT_4V_KEY, VISION_API_ENDPOINT, VISION_API_KEY, VIDEO_INDEX_NAME, VIDEO_FILE_SAS_URL, chat_history, question, document_id):
    # Configuration
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT_4V_KEY,
    }

    # Messages for payload
    messages = []
    if system_message is not None:
        messages.append(
            {
                "role": "system",
                "content": [
                    {
                            "type": "text",
                            "text": system_message
                    }
                ]
            }
        )

    if not chat_history:
        messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "acv_document_id",
                            "acv_document_id": document_id
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                        # question
                    ]
                }
            )
    else:
        add_doc = True
        for chat in chat_history:
            user_dict = {}
            user_dict['role'] = "user"
            user_dict['content'] = [{"type": "text", "text": chat['inputs']['question']}]
            if add_doc:
                user_dict['content'].append({"type": "acv_document_id", "acv_document_id": document_id})
                add_doc = False
            messages.append(user_dict)
            assitant_dict = {}
            assitant_dict['role'] = "assistant"
            assitant_dict['content'] = [{"type": "text", "text": chat['outputs']['answer']}]
            messages.append(assitant_dict)
        messages.append({"role": "user","content": [{"type": "text", "text": question}]})

    print(messages)
    # Payload for the request
    payload = {
        "dataSources": [
            {
                "type": "AzureComputerVisionVideoIndex",
                "parameters": {
                    "computerVisionBaseUrl": f"{VISION_API_ENDPOINT}/computervision",
                    "computerVisionApiKey": VISION_API_KEY,
                    "indexName": VIDEO_INDEX_NAME,
                    "videoUrls": [VIDEO_FILE_SAS_URL]
                }
            }
        ],
        "enhancements": {
            "video": {
                "enabled": True
            }
        },
        "messages": messages,
        "temperature": 0,
        "top_p": 0.95,
        "max_tokens": 100
    }

    try:
        
        response = requests.post(GPT_4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        response_message=response.json()['choices'][0]['message']['content']
        return response_message
    except requests.RequestException as e:
        print(e)
        traceback.print_stack()
        return "Error"
    

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(VIDEO_INDEX_NAME: str, VIDEO_FILE_SAS_URL: str, chat_history: list, conn: CustomConnection, question: str, document_id: str) -> str: #, is_video_indexed: bool) -> str:
    GPT_4V_ENDPOINT = conn.configs["GPT_4V_ENDPOINT"]
    GPT_4V_KEY = conn.secrets["GPT_4V_KEY"]
    VISION_API_KEY = conn.secrets["VISION_API_KEY"]
    VISION_API_ENDPOINT = conn.configs["VISION_API_ENDPOINT"]
    # if is_video_indexed:
    return call_gpt4v(GPT_4V_ENDPOINT, GPT_4V_KEY, VISION_API_ENDPOINT, VISION_API_KEY, VIDEO_INDEX_NAME, VIDEO_FILE_SAS_URL, chat_history, question, document_id)
    # else:
    #     return "Video is not indexed"

    