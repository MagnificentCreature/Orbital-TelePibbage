import requests
import json
from ImageGeneration import SDconf

AI_API_TOKEN = SDconf.key

url = "https://stablediffusionapi.com/api/v3/text2img"

PAYLOAD_TEMPLATE = json.dumps({
  "key": AI_API_TOKEN,
  "prompt": "ultra realistic close up portrait ((beautiful pale cyberpunk female with heavy black eyeliner))",
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
})

headers = {
  'Content-Type': 'application/json'
}

@staticmethod
async def imageQuery(prompt):
    payload = PAYLOAD_TEMPLATE
    payload.prompt = prompt
    response = requests.request("POST", url, headers=headers, data=payload)

    myDict = json.loads(response.text)

    return myDict["output"]
    


# if __name__ == '__main__':


#     response = requests.request("POST", url, headers=headers, data=payload)

#     print(response.text)
#     myDict = json.loads(response.text)
#     print(myDict["output"])
#     return
