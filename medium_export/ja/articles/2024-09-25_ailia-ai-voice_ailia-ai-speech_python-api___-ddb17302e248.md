---
title: "ailia AI Voiceとailia AI SpeechにPython APIを追加"
author: "Kazuki Kyakuno"
date: 2024-09-25
lastmod: 2024-11-01
original_url: https://tech.ailia.ai/ailia-ai-voiceとailia-ai-speechにpython-apiを追加-ddb17302e248
tags: [ailia-sdk]
---

# ailia AI Voiceとailia AI SpeechにPython APIを追加

# ailia AI Voiceとailia AI SpeechにPython APIを追加

[![Kazuki Kyakuno](../images/ailia-ai-voice_ailia-ai-speech_python-api___-ddb17302e248/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--ddb17302e248---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--ddb17302e248---------------------------------------)

7 min read

·

Sep 25, 2024

--

Share

音声合成を行うことができるailia AI Voiceと、音声認識を行うことができるailia AI SpeechにPython APIを追加しました。

Press enter or click to view image in full size

![](../images/ailia-ai-voice_ailia-ai-speech_python-api___-ddb17302e248/image_001.png)

ailia AI Voice and AI Speech for Python

## ailia AI Voiceとailia AI Speechについて

ailia AI VoiceはGPT-SoVITSを使用した音声合成を、ailia AI SpeechはWhisperを使用した音声認識を行うことができるライブラリです。

従来、これらのライブラリはC++、C#、Flutter向けのBindingを提供していましたが、新たにPython向けのBindingの提供を開始しました。

ailia AI Voiceとailia AI Speechは依存関係が非常に少なく、Pytorchを使用せずにONNXで動作するため、フレームワークのバージョンに依存しない安定した運用を実現します。また、Pythonでプロトタイピングした後に、UnityやFlutter向けのBindingを使用してiOSやAndroidのモバイルデバイスにデプロイすることも可能です。

## インストール

pipでインストール可能です。

```
pip3 install ailia_voice  
pip3 install ailia_speech
```

## 使用方法

ailia AI Voiceとailia AI SpeechのPython Bindingでは、非常に短いコードで音声合成と音声認識を実現します。モデルファイルも自動的にダウンロードされます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

ailia AI Voiceによる音声合成の使用方法は下記となります。reference\_audio\_girl.wavをダウンロードし、このファイルの声色を元に音声合成を行い、ファイルに保存します。

```
import ailia_voice  
  
import librosa  
import time  
import soundfile  
  
import os  
import urllib.request  
  
# Load reference audio  
ref_text = "水をマレーシアから買わなくてはならない。"  
ref_file_path = "reference_audio_girl.wav"  
if not os.path.exists(ref_file_path):  
 urllib.request.urlretrieve(  
  "https://github.com/axinc-ai/ailia-models/raw/refs/heads/master/audio_processing/gpt-sovits/reference_audio_captured_by_ax.wav",  
  "reference_audio_girl.wav"  
 )  
audio_waveform, sampling_rate = librosa.load(ref_file_path, mono=True)  
  
# Infer  
voice = ailia_voice.GPTSoVITS()  
voice.initialize_model(model_path = "./models/")  
voice.set_reference_audio(ref_text, ailia_voice.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA, audio_waveform, sampling_rate)  
buf, sampling_rate = voice.synthesize_voice("こんにちは。今日はいい天気ですね。", ailia_voice.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA)  
  
# Save result  
soundfile.write("output.wav", buf, sampling_rate)
```

ailia AI Speechによる音声認識の使用方法は下記となります。demo.wavをダウンロードし、このファイルに対して音声認識を行います。戻り値はgeneratorとなるため、長い音声でも認識結果を順番に取得可能です。

```
import ailia_speech  
  
import librosa  
  
import os  
import urllib.request  
  
# Load target audio  
input_file_path = "demo.wav"  
if not os.path.exists(input_file_path):  
 urllib.request.urlretrieve(  
  "https://github.com/axinc-ai/ailia-models/raw/refs/heads/master/audio_processing/whisper/demo.wav",  
  "demo.wav"  
 )  
audio_waveform, sampling_rate = librosa.load(input_file_path, mono=True)  
  
# Infer  
speech = ailia_speech.Whisper()  
speech.initialize_model(model_path = "./models/", model_type = ailia_speech.AILIA_SPEECH_MODEL_TYPE_WHISPER_MULTILINGUAL_SMALL)  
recognized_text = speech.transcribe(audio_waveform, sampling_rate)  
for text in recognized_text:  
  print(text)
```

## パラメータの指定

コンストラクタにailia SDKに渡すパラメータを指定可能です。GPUを使用する場合、下記のように設定します。

```
import ailia  
import ailia_voice  
import ailia_speech  
  
env_id = ailia.get_gpu_environment_id()  
voice = ailia_voice.GPTSoVITS(env_id = env_id)  
speech = ailia_speech.Whisper(env_id = env_id)
```

## オフラインでの動作

model\_pathにAIモデルのファイルが存在する場合、音声合成と音声認識が完全にオフラインで動作します。

## 音声認識の途中結果の表示

Whisperのcallbackに関数を与えることで、音声認識の途中結果を取得することが可能です。

```
import ailia_speech  
  
def f_callback(text):  
 print(text)  
  
speech = ailia_speech.Whisper(callback = f_callback)
```

## ドキュメント

基本的な使用方法はpypiのページを参照してください。

[## ailia-voice

### ailia AI Voice

pypi.org](https://pypi.org/project/ailia-voice/?source=post_page-----ddb17302e248---------------------------------------)

[## ailia-speech

### ailia AI Speech

pypi.org](https://pypi.org/project/ailia-speech/?source=post_page-----ddb17302e248---------------------------------------)

APIドキュメントは下記のailia-sdkのページを参照してください。

[## GitHub - axinc-ai/ailia-sdk: cross-platform high speed inference SDK

### cross-platform high speed inference SDK. Contribute to axinc-ai/ailia-sdk development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-sdk?source=post_page-----ddb17302e248---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。