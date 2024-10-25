import streamlit as st
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from pydub import AudioSegment
import tempfile
import uuid
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment variables from .env file
load_dotenv()

# Google Cloud credentialsの設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# OpenAI APIの設定
openai_api_key = os.getenv("OPENAI_API_KEY_STT")

# Google Cloud Storageの設定
bucket_name = os.getenv("GCS_BUCKET_NAME")
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# GCPにアップロードする準備
def upload_to_gcs(file):
    blob_name = f"audio_files/{str(uuid.uuid4())}"
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)
    return f"gs://{bucket_name}/{blob_name}"

# 音声から文字起こしする
def transcribe_gcs_audio(gcs_uri):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    # 各種設定
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ja-JP",
        enable_automatic_punctuation=True,
        use_enhanced=True,
        model="latest_long"
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    st.write("Transcription in progress. This may take a while...")
    result = operation.result()

    return result.results

def process_audio_file(uploaded_file):
    # 一時ファイルの作成、パスの取得
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file_path = temp_audio_file.name

    # audioの初期化
    if uploaded_file.name.lower().endswith('.m4a'):
        audio = AudioSegment.from_file(uploaded_file, format="m4a")
    else:
        audio = AudioSegment.from_file(uploaded_file)
    
    # プロパティの設定
    audio = audio.set_frame_rate(16000).set_channels(1)
    # wavで書き出す
    audio.export(temp_audio_file_path, format="wav")

    # GCPにアップロード
    with open(temp_audio_file_path, "rb") as audio_file:
        gcs_uri = upload_to_gcs(audio_file)

    # 一時ファイルの削除
    os.unlink(temp_audio_file_path)

    return gcs_uri

# OpenAI APIを使用して文章を要約する
def summarize_text(text):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたは優秀な編集者です。テキストを要約した後、要点を箇条書きしてください。"},
            {"role": "user", "content": f"以下の音声テキストを要約してください:\n\n{text}"}
        ],
        max_tokens=2048 
    )

    messages = response.choices[0].message.content

    return messages

# Streamlitの構成
st.title("Speech-to-Text App")

uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    # カウント開始
    start_time = time.time()
    
    with st.spinner("Processing audio file..."):
        gcs_uri = process_audio_file(uploaded_file)
    
    with st.spinner("Transcribing... This may take several minutes for long audio files."):
        results = transcribe_gcs_audio(gcs_uri)
    
    st.write("Transcription complete!")
    # 要約用の変数の初期化
    summary_transcript = ""
    for result in results:
        transcript = result.alternatives[0].transcript
        summary_transcript += transcript + " "
        st.write(transcript)
        st.write("---")
    
    with st.spinner("Summarizing the transcript..."):
        summary = summarize_text(summary_transcript)

    # 要約結果を表示
    st.subheader("Summary")
    st.write(summary)
    st.write("---")

    # カウント終了
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    hours, minutes = divmod(minutes, 60)

    # 実行時間の表示
    st.write(f"\rElapsed time: {hours:02}:{minutes:02}:{seconds:02}")

