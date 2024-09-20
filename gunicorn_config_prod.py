
# 実行するPythonがあるパス
pythonpath = './'

# ワーカー数
workers = 1

# ワーカーのクラス、*2 にあるようにUvicornWorkerを指定 (Uvicornがインストールされている必要がある)
worker_class = 'uvicorn.workers.UvicornWorker'

# IPアドレスとポート
bind = '127.0.0.1:8000'

# プロセスIDを保存するファイル名
pidfile = 'prod.pid'

# デーモン化する場合はTrue
daemon = True

# ログレベル
loglevel = 'DEBUG'
errorlog = './logs/error_log.txt'

# プロセスの名前
proc_name = 'style-bert-vits2-api'

# アクセスログ
accesslog = './logs/access_log.txt'