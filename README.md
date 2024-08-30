# 開発方法
Docker上での開発を想定しています。
vscodeの.devcontainerの設定が入っているので
vscodeでコンテナ起動して開発してください。

# 環境変数の設定
開発する場合は.envに下記を記載してdocker-compose経由で起動して実行。
```
ASSET_ROOT=/app/model_assets
MODE=cpu # gpu使えるならcuda 
PORT=8000
```

# モデルの設定
ASSET_ROOTの下に model名のフォルダを配置

必ず下記の構成にすること

```
ASSET_ROOT/
    model名/
        config.json
        ○○○.safetensors
        style_vectors.npy
```

# API呼び出し
api_call_sample.py を参照。

# deploy
各環境毎に上記の設定をしてください。


# 負荷試験
どれくらいパフォーマンス出るかk6のテストコード用意してあります。
```
k6 run --vus 10 --duration 30s load_test.js
```

GCPの
1 x NVIDIA T4
n1-standard-8
で上記程度の負荷であれば全然余裕。