import asyncio
import requests
import hashlib
import json
# import conf
import math

from GameController.Image import Image
from Player.PlayersManager import PlayersManager

# AI_API_TOKEN = conf.SD_API_TOKEN
AI_API_TOKEN = "7vFwuHHVpUoOW5his0TrwewJP40w1WDeydVQTMMllgzHBzjvLl6kcrqHGfTR"

URL_V3 = "https://stablediffusionapi.com/api/v3/text2img"
URL = "https://stablediffusionapi.com/api/v4/dreambooth"
FETCH_URL = "https://stablediffusionapi.com/api/v4/dreambooth/fetch"
CENSOR_HASH = "e9c4a470ad900801f7de4f9402eb27af8a1cc00eac80d618ef16bac39fb27d33"

MAX_RETRIES = 3
MAX_TIME = 120
EXTENDED_SLEEP = 10
ARCADE_EXTENDED_SLEEP = 15

PAYLOAD_DATA_TEMPLATE_V4 = {
  "key": AI_API_TOKEN,
  "model_id": "midjourney",
  "prompt": "",
  "negative_prompt": "",
  "width": "512",
  "height": "512",
  "samples": "1",
  "num_inference_steps": "30",
  "safety_checker": "yes",
  "enhance_prompt": "no",
  "seed": "",
  "guidance_scale": 7.5,
  "multi_lingual": "no",
  "webhook": "",
  "track_id": ""
}

# PAYLOAD_DATA_TEMPLATE_V4 = {
#   "key": AI_API_TOKEN,
#   "model_id": "midjourney", #anything_v4 is another possible model_id
#   "prompt": "",
#   "negative_prompt": "",
#   "width": "512",
#   "height": "512",
#   "samples": "1",
#   "num_inference_steps": "30",
#   "safety_checker": "yes",
#   "enhance_prompt": "no",
#   "seed": None,
#   "guidance_scale": 7.5,
#   "safety_checker": "yes",
#   "panorama": "no",
#   "self_attention": "no",
#   "upscale": "no",
#   "embeddings_model": None,
#   "lora_model": None,
#   "tomesd": "yes",
#   "use_karras_sigmas": "yes",
#   "vae": None,
#   "lora_strength": None,
#   "scheduler": "DDPMScheduler",
#   "webhook": None,
#   "track_id": None
# }

FETCH_PAYLOAD = {
 "key": AI_API_TOKEN,
 "request_id": "your_request_id"
}

PAYLOAD_DATA_TEMPLATE_V3 = {
  "key": AI_API_TOKEN,
  "prompt": "",
  "negative_prompt": None,
  "width": "512",
  "height": "512",
  "samples": "1",
  "num_inference_steps": "30",
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
def randomImage(author):
  payload = json.dumps(PAYLOAD_DATA_TEMPLATE_V3)
  myDict = sendHTTP(payload, URL_V3)
  if myDict["status"] == "failed":
    return None
  return errorChecking(myDict, myDict["meta"]["prompt"], author)

@staticmethod
def errorChecking(myDict, prompt, author):
  try:
    if myDict["status"] == "failed":
        return None
    if myDict["status"] == "processing":
        eta = math.ceil(float(myDict["eta"]))
        if eta > MAX_TIME:
            return None
        return Image(author, prompt, "", processingTime=eta, requestID=myDict["id"])
    if getImageHash(myDict["output"][0]) == CENSOR_HASH:
        return None
    return Image(author, prompt, myDict["output"][0])
  except KeyError:
    if myDict["message"] == "Server Error":
      print("Server Error")
    return None

@staticmethod
def sendHTTP(payload, url): 
  try:
    response = requests.request("POST", url, headers=headers, data=payload)
    myDict = json.loads(response.text)
    print(response.text)
    return myDict
  except IndexError:
    return None
  except requests.exceptions.RequestException as e:
    print("RequestException error " + e)
    return None

@staticmethod
async def imageQuery(prompt, author, safe=True):
  payload_data = PAYLOAD_DATA_TEMPLATE_V4.copy()
  payload_data["prompt"] = prompt
  if not safe:
    payload_data["safety_checker"] = "no"
  payload = json.dumps(payload_data)
  myDict = sendHTTP(payload, URL)
  return errorChecking(myDict, prompt, author)
    
@staticmethod
async def fetchImage(image, author, bot=None, retry_count = 0, arcade=False):
  payload_data = FETCH_PAYLOAD.copy()
  payload_data["request_id"] = image.getRequestID()
  payload = json.dumps(payload_data)
  myDict = sendHTTP(payload, FETCH_URL)

  player = PlayersManager.queryPlayer(author)

  if myDict["status"] == "processing":
    if retry_count >= MAX_RETRIES:
        if bot is not None:
          await player.sendMessage(bot, "MaxRetries")
        if arcade:
          return None
        return randomImage(author)
    if arcade:
      if bot is not None:
        await player.sendMessage(bot, "WaitingAgain", **{"time": 15, "retries": MAX_RETRIES - retry_count})
      await asyncio.sleep(ARCADE_EXTENDED_SLEEP) 
    else:
      if bot is not None:
        await player.sendMessage(bot, "WaitingAgain", **{"time": 10, "retries": MAX_RETRIES - retry_count})
      await asyncio.sleep(EXTENDED_SLEEP) 
    return await fetchImage(image, author, bot, retry_count + 1) #add await
  if getImageHash(myDict["output"][0]) == CENSOR_HASH:
    return None
  return Image(author, image.getPrompt(), myDict["output"][0])

# async def main():
  # image = await imageQuery("Misty, realistic mist, I want you to imagine spiderman with guns and Barak Obama, with racecars but Masterpiece and Studio Quality and 6k and there is a jungle in the background, the jungle is green and lush and they are having an epic ANIME battle, shot on a canon MAX", "GAY")
  # image = await imageQuery("hello im guy", "hi")
  # if image is not None and image.getProcessing() > 0:
  #   eta = image.getProcessing()
  #   await asyncio.sleep(eta/4)
  #   image = await fetchImage(image, "hi")
  # randomImage("gay")

# if __name__ == "__main__":
#   asyncio.run(imageQuery("", "hi"))
