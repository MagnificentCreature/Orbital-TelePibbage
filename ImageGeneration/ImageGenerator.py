import requests
import hashlib
import json
import conf

AI_API_TOKEN = conf.SD_API_TOKEN

URL = "https://stablediffusionapi.com/api/v3/text2img"
CENSOR_HASH = "e9c4a470ad900801f7de4f9402eb27af8a1cc00eac80d618ef16bac39fb27d33"

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
def getImageHash(imageUrl):
    response = requests.get(imageUrl)
    imageBytes = response.content
    return hashlib.sha256(imageBytes).hexdigest()
    
@staticmethod
async def imageQuery(prompt):
    payload_data = PAYLOAD_DATA_TEMPLATE.copy()
    payload_data["prompt"] = prompt
    payload = json.dumps(payload_data)

    response = requests.request("POST", URL, headers=headers, data=payload)
    myDict = json.loads(response.text)
    print(response.text)
    try :
      if getImageHash(myDict["output"][0]) == CENSOR_HASH:
          print("Image is censored")
          return None

      return myDict["output"][0]
    except IndexError:
      print()
      return None