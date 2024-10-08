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
Dockerを参考にしつつ
各環境毎に上記の設定をしてください。

gunicorn_config_prod.py を参照。
ワーカー数を環境によって変えてください。


```
pip install gunicorn
pip install setproctitle

# log dir 作成　
mkdir logs
# 起動
gunicorn -c gunicorn_config_prod.py main:app

# 停止
kill `cat prod.pid`

```


# 負荷試験
どれくらいパフォーマンス出るかk6のテストコード用意してあります。
```
k6 run --vus 10 --duration 30s load_test.js
```

GCPの
1 x NVIDIA T4
n1-standard-8
で上記程度の負荷であれば許容範囲(たまに4秒くらいかかっちゃうけど。大体1秒程度

<img width="832" alt="image" src="https://github.com/user-attachments/assets/f42f154c-da9e-42d7-99d0-e873e2adaedd">

<img width="678" alt="image" src="https://github.com/user-attachments/assets/16e6183f-2fb5-4161-8bec-60937463d161">

<img width="482" alt="image" src="https://github.com/user-attachments/assets/647b57e6-ea52-48df-bb23-cbe3c655cfdf">




メモリも全然問題なし。事前学習モデルのパターン増えない限り
モデルを追加しても影響ない。
```
2024-08-30 02:39:34,123 - INFO - メモリ使用量: RSS=2998.18 MB, VMS=17684.30 MB
```

# 費用感
大体1インスタスこれくらい。
¥50,080 / month

https://cloud.google.com/products/calculator?hl=ja&dl=CiQzYjlkNGI0ZC0zNzY4LTQ4YzMtOTFiOC0yNDc5NzdjMDRlYTMQCBokNjEwQTU3NzgtQzNEQy00MTE4LUI2N0QtRUQ2OEY4Q0NGNEU2



