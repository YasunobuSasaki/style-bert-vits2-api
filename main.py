# Hugging Faceから試しにデフォルトモデルをダウンロードしてみて、それを音声合成に使ってみる
# model_assetsディレクトリにダウンロードされます

from pathlib import Path
import subprocess
import tempfile
from huggingface_hub import hf_hub_download
from style_bert_vits2.tts_model import TTSModel
from pydantic import BaseModel
from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
import soundfile as sf
from fastapi import FastAPI
import base64
from fastapi.responses import JSONResponse
import io
import uvicorn
import os
import os
from dotenv import load_dotenv
load_dotenv()

import psutil
import logging
import socketio
import json
# ログの設定
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# メモリ使用量をログに記録する関数
def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logging.info(f"メモリ使用量: RSS={mem_info.rss / (1024 * 1024):.2f} MB, VMS={mem_info.vms / (1024 * 1024):.2f} MB")

####### style_bert_vits2の初期化処理

# モデルとトークナイザーをロード
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

# グローバルキャッシュ用の辞書
model_cache = {}

# アセットの配置場所
assets_root = Path(os.getenv("ASSET_ROOT"))

# assets_root下のディレクトリを全部ロード
from concurrent.futures import ThreadPoolExecutor

def load_model(model_dir):
    if model_dir.is_dir():
        try:
            model_name = model_dir.name
            # model_dir内の.safetensorsを検索し、はじめに見つかったファイルをmodel_pathとして取得
            model_path = None
            for file in model_dir.glob("*.safetensors"):
                model_path = file
                break
            if model_path is None:
                print(f"モデル {model_name} は存在しません。")
                return
            config_path = model_dir / "config.json"
            style_vec_path = model_dir / "style_vectors.npy"
            if not config_path.exists() or not style_vec_path.exists():
                print(f"モデル {model_name} は存在しません。")
                return
            
            model = TTSModel(
                model_path=model_path,
                config_path=model_dir / "config.json",
                style_vec_path=model_dir / "style_vectors.npy",
                device=os.getenv("MODE"),
            )
            model.infer(text="あ")
            # キャッシュに保存
            print(f"モデル {model_name} をloadしました。")
            model_cache[model_name] = model
        except Exception as e:
            print(f"モデル {model_name} のロード中にエラーが発生しました: {str(e)}")

with ThreadPoolExecutor() as executor:
    executor.map(load_model, assets_root.iterdir())


# メモリ使用量をログに記録
log_memory_usage()

###### APIサーバーの処理
app = FastAPI()

class InferRequest(BaseModel):
    model: str
    text: str
    format: str = "mp3"

@app.post("/infer")
async def infer(infer_request: InferRequest):
    model: TTSModel = get_model(infer_request.model)
    sr, audio = model.infer(text=infer_request.text)
    audio_io = io.BytesIO()
    sf.write(audio_io, audio, sr, format='WAV')
    audio_io.seek(0)
  
    
    # audio_base64 = base64.b64encode(audio_io.read()).decode('utf-8')
    # audio_io.seek(0)
    audio_base64 = ""
    if infer_request.format == "wav":
        audio_base64 = base64.b64encode(audio_io.read()).decode('utf-8')
        return JSONResponse(content={"audio_base64": audio_base64, "format": "wav"})
    
    # 一時ファイルにWAVを書き込む
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        temp_wav.write(audio_io.read())
        temp_wav_path = temp_wav.name

    # 一時ファイルにMP3を書き込む
    temp_mp3_path = temp_wav_path.replace(".wav", ".mp3")
    subprocess.run(["ffmpeg", "-i", temp_wav_path, "-acodec", "mp3", temp_mp3_path], check=True)

    # MP3ファイルを読み込んでBase64にエンコード
    with open(temp_mp3_path, "rb") as temp_mp3:
        audio_base64 = base64.b64encode(temp_mp3.read()).decode('utf-8')

    # 一時ファイルを削除
    os.remove(temp_wav_path)
    os.remove(temp_mp3_path)
    return JSONResponse(content={"audio_base64": audio_base64, "format": "mp3"})


@app.get("/models")
async def get_model_list():
    model_list = list(model_cache.keys())
    return JSONResponse(content={"models": model_list})


def get_model(model_name: str):
    if model_name in model_cache:
        return model_cache[model_name]
    else:
        return None

## socketio
sio = socketio.AsyncServer(async_mode='asgi')
app_socketio = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    await sio.emit('接続完了', {'メッセージ': 'サーバーに接続しました'}, room=sid)
    print('connect ', sid)

@sio.event
async def disconnect(sid):
    await sio.emit('接続解除', {'メッセージ': 'サーバーから切断しました'}, room=sid)
    print('disconnect ', sid)

class InferRequestSocket(BaseModel):
    key: str
    model: str
    text: str
@sio.event
async def message(sid, data):
    print(sid)
    try:
        data = json.loads(data)
        infer_request = InferRequest(model=data['model'], text=data['text'])
        model = get_model(infer_request.model)
        if model is None:
            await sio.emit('error', {'メッセージ': f'モデル {infer_request.model} は存在しません。'}, room=sid)
            return
        sr, audio = model.infer(text=infer_request.text)
        audio_io = io.BytesIO()
        sf.write(audio_io, audio, sr, format='WAV')
        audio_io.seek(0)
        audio_base64 = base64.b64encode(audio_io.read()).decode('utf-8')
        await sio.emit('infer', {'audio_base64': audio_base64, 'key': data['key']}, room=sid)
    except Exception as e:
        await sio.emit('error', {'メッセージ': '推論中にエラーが発生しました。', '詳細': str(e)}, room=sid)




if __name__ == "__main__":
    uvicorn.run(app_socketio, host="0.0.0.0", port=int(os.getenv("PORT")))