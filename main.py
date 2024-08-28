# Hugging Faceから試しにデフォルトモデルをダウンロードしてみて、それを音声合成に使ってみる
# model_assetsディレクトリにダウンロードされます

from pathlib import Path
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

####### style_bert_vits2の初期化処理

# モデルとトークナイザーをロード
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

# グローバルキャッシュ用の辞書
model_cache = {}

###### APIサーバーの処理
app = FastAPI()

class InferRequest(BaseModel):
    model: str
    text: str

@app.post("/infer")
async def infer(infer_request: InferRequest):
    assets_root = Path("model_assets")
    model_dir = assets_root / infer_request.model
    
    # モデルがキャッシュに存在するか確認
    if infer_request.model in model_cache:
        model = model_cache[infer_request.model]
    else:
        model = TTSModel(
            model_path=model_dir / "model.safetensors",
            config_path=model_dir / "config.json",
            style_vec_path=model_dir / "style_vectors.npy",
            device="cpu",
        )
        # キャッシュに保存
        model_cache[infer_request.model] = model
    
    sr, audio = model.infer(text=infer_request.text)
    audio_io = io.BytesIO()
    sf.write(audio_io, audio, sr, format='WAV')
    audio_io.seek(0)
    
    audio_base64 = base64.b64encode(audio_io.read()).decode('utf-8')
    
    return JSONResponse(content={"audio_base64": audio_base64})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)