---
title: "ailia SDKがFlutterのpubspecからインストール可能に"
author: "Kazuki Kyakuno"
date: 2025-12-31
original_url: https://tech.ailia.ai/ailia-sdkがflutterのpubspecからインストール可能に-f008229f7862
---

# ailia SDKがFlutterのpubspecからインストール可能に

# ailia SDKがFlutterのpubspecからインストール可能に

[![Kazuki Kyakuno](../images/ailia-sdk_flutter_pubspec___________-f008229f7862/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--f008229f7862---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--f008229f7862---------------------------------------)

9 min read

·

May 14, 2024

--

Share

ailia SDKがFlutterのpubspecを使用したインストールに対応しました。これにより、Flutterのアプリケーションに簡単にailia SDKを取り込み可能です。

Press enter or click to view image in full size

![]()

ailia x Flutter

## ailia SDKについて

ailia SDKはAIの推論エンジンで、ailia MODELSに公開されている各種のAIモデルを簡単にFlutterに取り込むことが可能です。開発したアプリケーションは、Windows、macOS、iOS、Android、Linuxで実行可能です。

## Flutterについて

FlutterはGoogleの開発している、クロスプラットフォームのアプリケーション開発環境です。Windows、macOS、iOS、Android、Linuxのアプリを、Dartを使用して、統一的に開発可能です。

[## Flutter - Build apps for any screen

### Flutter transforms the entire app development process. Build, test, and deploy beautiful mobile, web, desktop, and…

flutter.dev](https://flutter.dev/?source=post_page-----f008229f7862---------------------------------------)

## pubspecについて

pubspecはFlutterにおけるパッケージ管理ファイルです。pubspecにライブラリのURLを登録することで、簡単にアプリケーションにライブラリを追加可能です。

## pubspecを使用したailia SDKのインストール

pubspec.yamlに下記を記載します。flutter pub getで、必要なライブラリがインストールされます。

```
  ailia:  
    git:  
      url: https://github.com/ailia-ai/ailia-sdk-flutter.git  
      ref: main  
  
  ailia_audio:  
    git:  
      url: https://github.com/ailia-ai/ailia-audio-flutter.git  
      ref: main  
  
  ailia_tokenizer:  
    git:  
      url: https://github.com/ailia-ai/ailia-tokenizer-flutter.git  
      ref: main  
  
  ailia_speech:  
    git:  
      url: https://github.com/ailia-ai/ailia-speech-flutter.git  
      ref: main
```

macOSの場合は、ライセンスファイルにアクセスするために、macos/Runner/Release.entitlementsとmacos/Runner/Debug.entitlementsのcom.apple.security.app-sandboxをfalseに設定してください。

## ailia SDKを使用したサンプルプログラム

ailia SDKの使用方法のサンプルとして、ailia MODELS Flutterを提供しています。

[## GitHub - axinc-ai/ailia-models-flutter: ONNX Model Library for Flutter

### ONNX Model Library for Flutter. Contribute to axinc-ai/ailia-models-flutter development by creating an account on…

github.com](https://github.com/axinc-ai/ailia-models-flutter?source=post_page-----f008229f7862---------------------------------------)

現在、下記の4モデルに対応しています。モデルは、今後、随時、追加されていきます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

・ResNet18による物体識別  
・YOLOXによる物体認識  
・Whisperによる音声認識  
・MultilingualE5によるテキストのEmbedding

起動すると下記のような画面になります。

Press enter or click to view image in full size

![]()

モデルの選択

モデル一覧からモデルを選択し、プラスボタンを押すことで、モデルがダウンロードされ、推論が実行可能です。

Press enter or click to view image in full size

![]()

Whisperの実行例

特に、Whisperは非常に短いコードで実行可能で、簡単にFlutterのアプリケーションに音声認識を実装可能です。

```
import 'dart:io';  
  
import 'package:flutter/material.dart';  
import 'package:wav/wav.dart';  
  
import 'package:flutter/services.dart';  
import 'package:ailia_speech/ailia_speech.dart' as ailia_speech_dart;  
import 'package:ailia_speech/ailia_speech_model.dart';  
  
class AudioProcessingWhisper {  
  final AiliaSpeechModel _ailiaSpeechModel = AiliaSpeechModel();  
  
  void _intermediateCallback(String text){  
  }  
  
  Future<String> transcribe(Wav wav, File onnx_encoder_file, File onnx_decoder_file, int env_id) async{  
    _ailiaSpeechModel.create(false, false, env_id);  
    _ailiaSpeechModel.open(onnx_encoder_file, onnx_decoder_file, null, "auto", ailia_speech_dart.AILIA_SPEECH_MODEL_TYPE_WHISPER_MULTILINGUAL_TINY);  
  
    List<double> pcm = List<double>.empty(growable: true);  
  
    for (int i = 0; i < wav.channels[0].length; ++i) {  
      for (int j = 0; j < wav.channels.length; ++j){  
        pcm.add(wav.channels[j][i]);  
      }  
    }  
  
    //_ailiaSpeechModel.setIntermediateCallback(_intermediateCallback);  
    _ailiaSpeechModel.pushInputData(pcm, wav.samplesPerSecond, wav.channels.length);  
  
    _ailiaSpeechModel.finalizeInputData();  
  
    String transcribe_result = "";  
  
    List<SpeechText> texts = _ailiaSpeechModel.transcribeBatch();  
    for (int i = 0; i < texts.length; i++){  
      transcribe_result = transcribe_result + texts[i].text;  
    }  
  
    _ailiaSpeechModel.close();  
  
    return transcribe_result;  
  }  
  
}
```

[## ailia-models-flutter/lib/audio\_processing/whisper.dart at main · axinc-ai/ailia-models-flutter

### ONNX Model Library for Flutter. Contribute to axinc-ai/ailia-models-flutter development by creating an account on…

github.com](https://github.com/axinc-ai/ailia-models-flutter/blob/main/lib/audio_processing/whisper.dart?source=post_page-----f008229f7862---------------------------------------)

また、Multilingual E5を使用することで、FlutterでRAGを簡単に実装可能です。ailia SDKはailia Tokenizerを提供しているため、日本語のテキストから、簡単にEmbeddingを取得可能です。

[## ailia-models-flutter/lib/natural\_language\_processing/multilingual\_e5.dart at main ·…

### ONNX Model Library for Flutter. Contribute to axinc-ai/ailia-models-flutter development by creating an account on…

github.com](https://github.com/axinc-ai/ailia-models-flutter/blob/main/lib/natural_language_processing/multilingual_e5.dart?source=post_page-----f008229f7862---------------------------------------)

## ライセンスファイルについて

ailia SDKの評価版の利用にはライセンスファイルが必要です。ライセンスファイルは下記のコードでダウンロード可能です。ailia MODELS Flutterには下記のコードが含まれています。

```
import 'package:ailia/ailia_license.dart';  
await AiliaLicense.checkAndDownloadLicense();
```

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。