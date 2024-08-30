# Hugging Faceから試しにデフォルトモデルをダウンロードしてみて、それを音声合成に使ってみる
# model_assetsディレクトリにダウンロードされます

import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from style_bert_vits2.tts_model import TTSModel

from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
import soundfile as sf


# モデルとトークナイザーをロード
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")


model_file = "jvnv-F1-jp/jvnv-F1-jp_e160_s14000.safetensors"
config_file = "jvnv-F1-jp/config.json"
style_file = "jvnv-F1-jp/style_vectors.npy"
local_dir = "model_assets"

for file in [model_file, config_file, style_file]:
    if Path(f"{local_dir}/{file}").exists():
        continue
    print(file)
    hf_hub_download("litagin/style_bert_vits2_jvnv", file, local_dir=local_dir)


# 上でダウンロードしたモデルファイルを指定して音声合成のテスト
assets_root = Path(local_dir)
print(assets_root)
print(assets_root / model_file)
print(assets_root / config_file)
print(assets_root / style_file)
model = TTSModel(
    model_path=assets_root / model_file,
    config_path=assets_root / config_file,
    style_vec_path=assets_root / style_file,
    device=os.getenv("MODE"),
)

sr, audio = model.infer(text="こんにちは！")

audio_path = "audio.wav"
# 音声ファイルを保存
sf.write(audio_path, audio, sr)
