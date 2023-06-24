import requests
import hashlib
import json
# import conf
import math

AI_API_TOKEN = "7vFwuHHVpUoOW5his0TrwewJP40w1WDeydVQTMMllgzHBzjvLl6kcrqHGfTR"
# AI_API_TOKEN = conf.SD_API_TOKEN

URL = "https://stablediffusionapi.com/api/v4/dreambooth"
FETCH_URL = "https://stablediffusionapi.com/api/v4/dreambooth/fetch"
CENSOR_HASH = "e9c4a470ad900801f7de4f9402eb27af8a1cc00eac80d618ef16bac39fb27d33"

PAYLOAD_DATA_TEMPLATE_V4 = {
  "key": AI_API_TOKEN,
  "model_id": "midjourney", #anything_v4 is another possible model_id
  "prompt": "",
  "negative_prompt": "",
  "width": "512",
  "height": "512",
  "samples": "1",
  "num_inference_steps": "30",
  "safety_checker": "yes",
  "enhance_prompt": "yes",
  "seed": None,
  "guidance_scale": 7.5,
  "multi_lingual": "no",
  "panorama": "no",
  "self_attention": "no",
  "upscale": "no",
  "embeddings_model": None,
  "lora_model": None,
  "tomesd": "yes",
  "use_karras_sigmas": "yes",
  "vae": None,
  "lora_strength": None,
  "scheduler": "UniPCMultistepScheduler",
  "webhook": None,
  "track_id": None
}

FETCH_PAYLOAD = {
 "key": AI_API_TOKEN,
 "request_id": "your_request_id"
}

# PAYLOAD_DATA_TEMPLATE_V3 = {
#   "key": AI_API_TOKEN,
#   "prompt": "",
#   "negative_prompt": None,
#   "width": "512",
#   "height": "512",
#   "samples": "1",
#   "num_inference_steps": "20",
#   "seed": None,
#   "guidance_scale": 7.5,
#   "safety_checker": "yes",
#   "multi_lingual": "no",
#   "panorama": "no",
#   "self_attention": "no",
#   "upscale": "no",
#   "embeddings_model": "embeddings_model_id",
#   "webhook": None,
#   "track_id": None
# }

headers = {
  'Content-Type': 'application/json'
}

@staticmethod
def getImageHash(imageUrl):
    response = requests.get(imageUrl)
    imageBytes = response.content
    return hashlib.sha256(imageBytes).hexdigest()
    
@staticmethod
def imageQuery(prompt):
    payload_data = PAYLOAD_DATA_TEMPLATE_V4.copy()
    payload_data["prompt"] = prompt
    payload = json.dumps(payload_data)
    try:
      response = requests.request("POST", URL, headers=headers, data=payload)
      myDict = json.loads(response.text)
      print(response.text)
      if myDict["status"] == "processing":
        print("Image is processing")
        eta = math.ceil(float(myDict["eta"]))
        return str(myDict["id"]) + ":" + str(eta)
      if getImageHash(myDict["output"][0]) == CENSOR_HASH:
          print("Image is censored")
          return None
      return myDict["output"][0]
    except IndexError:
      print(response.text)
      return None
    except requests.exceptions.RequestException as e:
      print("RequestException error " + e)
      return None
    
@staticmethod
async def fetchImage(request_id):
   payload_data = FETCH_PAYLOAD.copy()
   payload_data["request_id"] = request_id
   payload = json.dumps(payload_data)
   response = requests.request("POST", FETCH_URL, headers=headers, data=payload)
   myDict = json.loads(response.text)
   print(response.text)
   if getImageHash(myDict["output"][0]) == CENSOR_HASH:
      print("Image is censored")
      return None
   return myDict["output"][0]

if __name__ == "__main__":
  imageQuery("giant painting on an exquisite wall in the middle of a grassland, there is a giant mansion in the background and its mysterious, shot on a cannon POV")
