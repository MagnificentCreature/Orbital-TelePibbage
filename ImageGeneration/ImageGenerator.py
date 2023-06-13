import requests
import json
import conf

AI_API_TOKEN = conf.SD_API_TOKEN

URL = "https://stablediffusionapi.com/api/v3/text2img"

PAYLOAD_DATA_TEMPLATE = {
  "key": AI_API_TOKEN,
  "prompt": "",
  "negative_prompt": None,
  "width": "512",
  "height": "512",
  "samples": "1",
  "num_inference_steps": "20",
  "seed": None,
  "guidance_scale": 7.5,
  "safety_checker": "yes",
  "multi_lingual": "no",
  "panorama": "no",
  "self_attention": "no",
  "upscale": "no",
  "embeddings_model": "embeddings_model_id",
  "webhook": None,
  "track_id": None
}

headers = {
  'Content-Type': 'application/json'
}

@staticmethod
async def imageQuery(prompt):
    payload_data = PAYLOAD_DATA_TEMPLATE.copy()
    payload_data["prompt"] = prompt
    payload = json.dumps(payload_data)

    response = requests.request("POST", URL, headers=headers, data=payload)
    myDict = json.loads(response.text)
    print(response.text)

    return myDict["output"][0]