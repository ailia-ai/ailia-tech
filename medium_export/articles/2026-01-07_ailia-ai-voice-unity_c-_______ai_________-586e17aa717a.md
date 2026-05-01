---
title: "ailia AI Voice : UnityやC++から使用できるAI音声合成ライブラリ"
author: "Kazuki Kyakuno"
date: 2026-01-07
original_url: https://tech.ailia.ai/ailia-ai-voice-unityやc-から使用できるai音声合成ライブラリ-586e17aa717a
---

# ailia AI Voice : UnityやC++から使用できるAI音声合成ライブラリ

# ailia AI Voice : UnityやC++から使用できるAI音声合成ライブラリ

[![Kazuki Kyakuno](../images/ailia-ai-voice-unity_c-_______ai_________-586e17aa717a/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--586e17aa717a---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--586e17aa717a---------------------------------------)

21 min read

·

Jun 19, 2024

--

Share

UnityやC++から使用できるAI音声合成ライブラリであるailia AI Voiceのご紹介です。ailia AI Voiceを使用することで、簡単にアプリケーションにAI音声合成を実装することが可能です。

## ailia AI Voiceの概要

ailia AI Voiceは、AIを使用した音声合成を行うためのライブラリです。Unity向けのC#のAPIと、ネイティブアプリ向けのCおよびFlutterのAPI、PC向けのPythonのAPIを提供します。ailia AI Voiceを使用することで、AIを使用した音声合成を簡単にアプリケーションに実装することが可能です。

Press enter or click to view image in full size

![]()

ailia AI Voice

ailia AI Voiceは、クラウド接続不要で、エッジ端末だけでオフラインで音声合成を行うことが可能です。また、最新のGPT-SoVITSに対応しており、任意の声色での音声合成が可能です。

## ailiaAI Voiceの特徴

### 多言語に対応

英語の音声合成モデルと、日本語の音声合成モデルを使用可能です。英語向けにはTacotron2のNVIDIAの公式モデル、日本語向けにはGPT-SoVITSの公式モデルを提供しています。

### オフラインで動作

クラウド不要で端末だけで音声合成を実行可能です。また、CPUだけでも推論が可能です。

### モバイルデバイス対応

PCだけでなく、iOSやAndroidのモバイルデバイスでも音声合成が実行可能です。

### UnityおよびFlutter対応

C APIに加えて、Unity PluginおよびFlutter Bindingを提供しているため、UnityやFlutterを使用したアプリケーションに簡単に音声合成を実装可能です。

### 任意の声色での音声合成に対応

GPT-SoVITSを使用することで、10秒程度の音声ファイルを与えることで、任意の声色で音声合成を行うことが可能です。

## ailia AI Voiceのアーキテクチャ

ailia AI Voiceでは、音声合成のアルゴリズムに[Tacotron2](https://github.com/NVIDIA/tacotron2)と、[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)を選択可能です。Tacotron2とGPT-SoVITSで日本語を使用するには、日本語のテキストを音素に変換する必要があり、G2Pの機能をailia AI Voiceのライブラリに内蔵しています。これにより、Windows、macOS、Linux、iOS、Androidで使用可能です。

Press enter or click to view image in full size

![]()

アーキテクチャ

## ailia AI Voiceの使用方法

C#を使用して音声合成をする例です。AiliaVoiceModelを作成し、OpenDictionaryで辞書を、OpenModelでAIモデルを読み込み、G2Pでテキストを音素に変換、Inferenceを呼び出すことでAudioClipを取得可能です。GPT-SoVITSの場合は、リファレンスとなる10秒程度の音声ファイルと、対応するテキストを与えることで、任意の声色で音声合成可能です。

```
void Initialize(){  
    bool status = voice.Create(Ailia.AILIA_ENVIRONMENT_ID_AUTO, AiliaVoice.AILIA_VOICE_FLAG_NONE);  
  
    string asset_path=Application.streamingAssetsPath;  
  
    string path = asset_path+"/AiliaVoice/";  
    status = voice.OpenDictionary(path+"open_jtalk_dic_utf_8-1.11", AiliaVoice.AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK);  
  
    switch(model){  
    case MODEL_TACOTRON2_ENGLISH:  
        status = voice.OpenModel(path+"onnx/nvidia/encoder.onnx", path+"onnx/nvidia/decoder_iter.onnx", path+"onnx/nvidia/postnet.onnx", path+"onnx/nvidia/waveglow.onnx", null, AiliaVoice.AILIA_VOICE_MODEL_TYPE_TACOTRON2, AiliaVoice.AILIA_VOICE_CLEANER_TYPE_BASIC);  
        break;  
    case MODEL_GPT_SOVITS_JAPANESE:  
        status = voice.OpenModel(path+"onnx/gpt-sovits/t2s_encoder.onnx", path+"onnx/gpt-sovits/t2s_fsdec.onnx", path+"onnx/gpt-sovits/t2s_sdec.opt.onnx", path+"onnx/gpt-sovits/vits.onnx", path+"onnx/gpt-sovits/cnhubert.onnx", AiliaVoice.AILIA_VOICE_MODEL_TYPE_GPT_SOVITS, AiliaVoice.AILIA_VOICE_CLEANER_TYPE_BASIC);  
        break;  
    }  
 }  
  
 void Infer(string text){  
    if (model == MODEL_GPT_SOVITS_JAPANESE){  
        text = voice.G2P(text, AiliaVoice.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA);  
        string ref_text = voice.G2P("水をマレーシアから買わなくてはならない。", AiliaVoice.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA);  
        voice.SetReference(ref_clip, ref_text);  
    }  
  
    voice.Inference(text);  
      
    audioSource.clip = voice.GetAudioClip();  
    audioSource.Play();  
}  
  
void Uninitialize(){  
    voice.Close();  
}
```

非同期で音声合成を行いたい場合は、Taskを使用することもできます。なお、複数のスレッドから同時にInferenceを行うと例外が発生しますので、上層で排他制御を行ってください。また、AudioClipはサブスレッドからは操作できないため、SetReferenceとGetAudioClipはメインスレッドで操作する必要があります。

```
using System.Threading;  
using System.Threading.Tasks;  
  
void Infer(string text){  
  var context = SynchronizationContext.Current;  
  Task.Run(async () =>  
  {  
   string feature = voice.G2P(text, AiliaVoice.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA);  
   bool status = voice.Inference(feature);  
   context.Post(state =>  
   {  
    clip = voice.GetAudioClip();  
    audioSource.clip = clip;  
    audioSource.Play();  
   }, null);     
  });//.Wait();  
}
```

## 合成音声のサンプル

Tacotron2の英語音声のサンプルは下記となります。  
<https://storage.googleapis.com/ailia-models/blog/tacotron2.wav>

GPT-SoVITSの日本語音声のサンプルは下記となります。<https://storage.googleapis.com/ailia-models/blog/gpt-sovits.wav>

ailia AI Voiceを使用することで、最新の音声合成モデルを使用した、自然な音声合成が可能です。

## 声質のリファレンスとなる音声について

GPT-SoVITSは10秒程度の音声を与えることで、その声質で音声合成が可能です。その際、無音区間が長い音声を与えると不安定になる場合があるので、無音部分を手動で削除した音声ファイルを与えることが望ましいです。また、喋っているテキストの末尾には「。」がある方が安定します。

## モデルサイズと推論速度

Tacotron2のモデルは、音素からパワースペクトルを計算するモデルが112MB、パワースペクトルから位相を計算して波形に戻すモデルが312MBとなっています。

GPT-SoVITSのモデルは、特徴抽出が377MB、エンコーダが11MB、デコーダが615MB、音声変換が162MBとなります。

macOSのM3のCPUで、GPT-SoVITSを使用した場合、2.9秒の音声を2.8秒程度で音声合成可能です。また、さらに多くのデバイスでリアルタイム推論を可能とするための高速化を進めています。

## ailia AI Voiceの評価版とドキュメント

ailia AI Voiceの評価版は下記からダウンロード可能です。

[## AILIA-VOICE 評価ライセンス申し込み

### ailia評価版使用許諾契約書 …

axip-console.appspot.com](https://axip-console.appspot.com/trial/terms/AILIA-VOICE?source=post_page-----586e17aa717a---------------------------------------)

APIドキュメントは下記から参照可能です。

[## GitHub - ailia-ai/ailia-sdk: ailia SDK Documentation

### ailia SDK Documentation. Contribute to ailia-ai/ailia-sdk development by creating an account on GitHub.

github.com](https://github.com/ailia-ai/ailia-sdk?source=post_page-----586e17aa717a---------------------------------------)

## ailia AI Voiceのデモアプリ

macOSで実行可能なailia AI Voiceのデモアプリは下記からダウンロード可能です。

[## AILIA-VOICE 1.4.0\_demo\_mac ダウンロード

### Edit description

axip-console.appspot.com](https://axip-console.appspot.com/binary/download/ndb_MTc2Nzc1MzY5NS43Njg1MjU0XzY5MzkyODM3MA==?source=post_page-----586e17aa717a---------------------------------------)

起動後、モデルが自動的にダウンロードされます。テキストボックスにテキストを入力し、Speakで音声合成が可能です。Tacotron2では英語が、GPT-SoVITSでは日本語が使用可能です。

Press enter or click to view image in full size

![]()

デモアプリの実行例

起動時に「不正なバイナリ」と表示される場合は、下記のコマンドでダウンロード属性を解除してください。

```
xattr -d com.apple.quarantine ailia_voice_sample.app
```

## チュートリアル

### Unityから使用する（Unity Package）

ailia AI Voiceの評価版にはUnity Packageが含まれています。Unity Packageのサンプルでは、任意のテキストから音声合成を行い、再生を行うことが可能です。

Press enter or click to view image in full size

![]()

ailia AI Voiceのサンプルプログラム

ailia AI VoiceのUnity Packageをインポートした後、Package Managerで下記の依存ライブラリをインストールしてください。ライセンスファイルは自動的にダウンロードされます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

[ailia SDK](https://github.com/axinc-ai/ailia-sdk-unity)（コアモジュール）  
https://github.com/ailia-ai/ailia-sdk-unity.git

[ailia Audio](https://github.com/axinc-ai/ailia-audio-unity)（音声処理に必要）  
https://github.com/ailia-ai/ailia-audio-unity.git

Press enter or click to view image in full size

![]()

ailia SDKとailia AudioをPackage Managerに追加

### Unityから使用する（Package Manager + ailia MODELS Unity）

ailia MODELS Unityからも使用可能です。ailia MODELS Unityでは、下記のパッケージを参照しています。

[ailia Voice](https://github.com/axinc-ai/ailia-voice-unity)（音声合成モジュール）  
https://github.com/ailia-ai/ailia-voice-unity.git

ailia MODELS Unityに含まれるTextToSpeech.sceneを使用することで、音声合成を使用可能です。

[## GitHub — axinc-ai/ailia-models-unity: Unity version of ailia models repository

### Unity version of ailia models repository. Contribute to axinc-ai/ailia-models-unity development by creating an account…

github.com](https://github.com/axinc-ai/ailia-models-unity?source=post_page-----586e17aa717a---------------------------------------)

Press enter or click to view image in full size

![]()

ailia MODELS Unityの中のTextToSpeech.scene

ailia MODELS Unityの場合、Tacotron2とGPT-SoVITSはInspectorで切り替え可能です。また、ref\_clipに声質のリファレンスとなる音源を設定可能です。「水をマレーシアから買わなくてはならない。」と喋っている音声を与えることで、その声質を利用可能です。その他のテキストの音声で声質を設定する場合は、AiliaVoiceSample.csのテキストを喋っているテキストで書き換えてください。

![]()

Reference Clipの設定

なお、GPT SoVitsは毎フレーム、Shapeが変化する関係で、現状、GPUよりもCPUの方が動作が高速です。将来的に、GPU向けの最適化が実装される予定です。

ailia AI Voiceの使用にはailia SDK 1.4.0以降が必要です。実行時にエラーが発生する場合は、Package Managerで1.4.0以上になっているか確認してください。

Press enter or click to view image in full size

![]()

### C++から使用する

SDKを展開後、cppフォルダで下記のコマンドでビルドします。ライセンスファイルが存在しないとエラー（-20）が発生するため、ライセンスファイルをcppフォルダにコピーしてください。

Windows

```
cl ailia_voice_sample.cpp wave_writer.cpp wave_reader.cpp ailia_voice.lib ailia.lib ailia_audio.lib
```

macOS

```
clang++ -o ailia_voice_sample ailia_voice_sample.cpp wave_writer.cpp wave_reader.cpp libailia_voice.dylib libailia.dylib libailia_audio.dylib -Wl,-rpath,./ -std=c++17
```

Linux

```
g++ -o ailia_voice_sample ailia_voice_sample.cpp wave_writer.cpp wave_reader.cpp libailia_voice.so libailia.so libailia_audio.so
```

実行

```
./ailia_voice_sample tacotron2  
./ailia_voice_sample gpt-sovits
```

### Flutterから使用する（pubspec）

pubspec.yamlに下記を追加します。

```
  ailia:  
    git:  
      url: https://github.com/ailia-ai/ailia-sdk-flutter.git  
  
  ailia_audio:  
    git:  
      url: https://github.com/ailia-ai/ailia-audio-flutter.git  
  
  ailia_voice:  
    git:  
      url: https://github.com/ailia-ai/ailia-voice-flutter.git
```

下記のコードで音声合成を行います。

```
  Future<void> inference(  
      String targetText,  
      String outputPath,  
      String encoderFile,  
      String decoderFile,  
      String postnetFile,  
      String waveglowFile,  
      String? sslFile,  
      String dicFolder,  
      int modelType) async {  
    _ailiaVoiceModel.open(  
        encoderFile,  
        decoderFile,  
        postnetFile,  
        waveglowFile,  
        sslFile,  
        dicFolder,  
        modelType,  
        ailia_voice_dart.AILIA_VOICE_CLEANER_TYPE_BASIC,  
        ailia_voice_dart.AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK,  
        ailia_voice_dart.AILIA_ENVIRONMENT_ID_AUTO);  
  
    if (modelType == ailia_voice_dart.AILIA_VOICE_MODEL_TYPE_GPT_SOVITS) {  
      ByteData data = await rootBundle.load("assets/reference_audio_girl.wav");  
      final wav = Wav.read(data.buffer.asUint8List());  
  
      List<double> pcm = List<double>.empty(growable: true);  
  
      for (int i = 0; i < wav.channels[0].length; ++i) {  
        for (int j = 0; j < wav.channels.length; ++j) {  
          pcm.add(wav.channels[j][i]);  
        }  
      }  
  
      String referenceFeature = _ailiaVoiceModel.g2p("水をマレーシアから買わなくてはならない。",  
          ailia_voice_dart.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA);  
      _ailiaVoiceModel.setReference(  
          pcm, wav.samplesPerSecond, wav.channels.length, referenceFeature);  
    }  
  
    String targetFeature = targetText;  
    if (modelType == ailia_voice_dart.AILIA_VOICE_MODEL_TYPE_GPT_SOVITS) {  
      targetFeature = _ailiaVoiceModel.g2p(targetText,  
          ailia_voice_dart.AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA);  
    }  
    final audio = _ailiaVoiceModel.inference(targetFeature);  
    _speaker.play(audio, outputPath);  
  
    _ailiaVoiceModel.close();  
  }  
}
```

[## ailia-voice-flutter/example/lib at main · ailia-ai/ailia-voice-flutter

### ailia AI Voice Flutter Binding. Contribute to ailia-ai/ailia-voice-flutter development by creating an account on…

github.com](https://github.com/ailia-ai/ailia-voice-flutter/tree/main/example/lib?source=post_page-----586e17aa717a---------------------------------------)

### Flutterから使用する（ailia MODELS Flutter）

ailia MODELS Flutterからも使用可能です。下記のリポジトリをクローンして実行します。

[## GitHub - ailia-ai/ailia-models-flutter: ONNX Model Library for Flutter

### ONNX Model Library for Flutter. Contribute to ailia-ai/ailia-models-flutter development by creating an account on…

github.com](https://github.com/ailia-ai/ailia-models-flutter?source=post_page-----586e17aa717a---------------------------------------)

ailia AI Voiceの利用にはailia SDK 1.4.0以降が必要です。下記のコマンドでアップデートしてください。

```
flutter pub upgrade
```

ailia MODELS Flutterを実行すると、モデルリストからTacotron2とGPT-SoVITSを選択可能です。プラスボタンを押して推論を開始します。

## Pythonから使用する

Pythonから使用する場合、pipでailia\_voiceをインストールします。

```
pip3 install ailia_voice
```

下記のコードで音声合成が可能です。

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

アイリア株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。アイリア株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://ailia.ai/contact/)ください。