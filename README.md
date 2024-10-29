# 概要
StreamlitでSpeech-to-text APIを使用した音声文字起こしアプリ
## 機能
mp3,wav,m4a等の音声データを文字に起こし、AIで要約します。
## 事前に行うこと
### dotenv
python-dotenvを使用してます。
.envファイルを作成したうえで、任意の定数を定義してください。
### GCP
Google Cloud Platformを使用します。<br>
Speech-to-textとCloud Storageを有効にしてください。<br>
GCPのセットアップは割愛します。
### OpenAI API
OpenAIのAPIを使用しています。
セットアップは割愛します。
### インストール系
- インストールするパッケージについては、requirements.txtを参照してください
- ffmpegのインストール
音声処理を行うためにWindowsにffmpegをインストールする必要があります。<br>
URL（https://www.ffmpeg.org/download.html）でffmpegをインストール及び解凍します。<br>
その後、"path\hoge\ffmpeg-master-hoge\bin"のところまでパスをコピーし、環境変数のpathに追加します。
### ファイル
- .streamlitフォルダのconfig.tomlでは、fileuploaderのデータ上限を設定しています。必要に応じて数値を変更してください。
- .envファイルを作成して、定数"GOOGLE_APPLICATION_CREDENTIALS"、"OPENAI_API_KEY_STT"、"GCS_BUCKET_NAME"を定義してください。
## その他
- transcribe_gcs_audio(gcs_uri)のconfigのmodelについては、latest-longを使用していますが、必要に応じて変更してください。
