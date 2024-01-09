from promptflow import tool
from promptflow.connections import CustomConnection
import json
import requests
import time, os

def create_video_index(vision_api_endpoint, vision_api_key, index_name):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}?api-version=2023-05-01-preview"
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key, "Content-Type": "application/json"}
    data = {
        "features": [
            {"name": "vision", "domain": "surveillance"}
        ]
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response

def add_video_to_index(vision_api_endpoint, vision_api_key, index_name, video_url, video_id):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}/ingestions/my-ingestion-divye?api-version=2023-05-01-preview"
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key, "Content-Type": "application/json"}
    data = {
        'videos': [{'mode': 'add', 'documentId': video_id, 'documentUrl': video_url}]
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response

def wait_for_ingestion_completion(vision_api_endpoint, vision_api_key, index_name, max_retries=50):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{index_name}/ingestions?api-version=2023-05-01-preview"
    headers = {"Ocp-Apim-Subscription-Key": vision_api_key}
    retries = 0
    while retries < max_retries:
        time.sleep(10)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            state_data = response.json()
            if state_data['value'][0]['state'] == 'Completed':
                print(state_data)
                print('Ingestion completed.')
                return True
        retries += 1
    return False

if __name__ == "__main__":
    #read environment variables
    vision_api_endpoint = os.environ["VISION_API_ENDPOINT"]
    vision_api_key = os.environ["VISION_API_KEY"]
    video_index_name = "my-video-index"
    video_sas_url = "SAS_UTL of video"
    video_id = "my-video-id"
    create_video_index(vision_api_endpoint, vision_api_key, video_index_name)
    add_video_response = add_video_to_index(vision_api_endpoint, vision_api_key, video_index_name, video_sas_url, video_id)
    wait_for_indexer_response = wait_for_ingestion_completion(vision_api_endpoint, vision_api_key, video_index_name)


# @tool
# def my_python_tool(video_sas_url: str, video_index_name:str, video_id: str, conn: CustomConnection, index: bool) -> str:
#     response = True
#     if index:
#         vision_api_endpoint = conn.configs["VISION_API_ENDPOINT"]
#         vision_api_key = conn.secrets["VISION_API_KEY"]
#         creation_response = create_video_index(vision_api_endpoint, vision_api_key, video_index_name)
#         print(creation_response.__dict__)
#         # if creation_response.status_code == 201:
#         print('Index created.')
#         add_video_response = add_video_to_index(vision_api_endpoint, vision_api_key, video_index_name, video_sas_url, video_id)
#         print(add_video_response.__dict__)
#         print('Video added to index.')
#         wait_for_indexer_response = wait_for_ingestion_completion(vision_api_endpoint, vision_api_key, video_index_name)
#         if wait_for_indexer_response:
#             print('Ingestion completed.')
#         else:
#             print('Ingestion failed.')
#             response = False
#     return response