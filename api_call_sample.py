import requests
import json

url = "http://localhost:8000/infer"

payload = json.dumps({
  "model": "jvnv-F1-jp",
  "text": "いぇーい"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

response_json = response.json()


import base64

audio_base64 = response_json.get('audio_base64')
if audio_base64:
    audio_data = base64.b64decode(audio_base64)
    with open('output.wav', 'wb') as wav_file:
        wav_file.write(audio_data)

