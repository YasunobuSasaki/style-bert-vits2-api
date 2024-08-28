# モデルの設定
model_assetsをルート直下に作成し
その下に model名のフォルダを配置

必ず下記の構成にすること

```
 model名/
    config.json
    model.safetensors
    style_vectors.npy
```

# API呼び出し
api_call_sample.py を参照。
