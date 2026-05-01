---
title: "ailia SDKを使用してFlutterでONNX形式のAIモデルを推論する"
author: "Kazuki Kyakuno"
date: 2024-10-16
original_url: https://tech.ailia.ai/ailia-sdkを使用してflutterでonnx形式のaiモデル推論する-7c68509b296
---

# ailia SDKを使用してFlutterでONNX形式のAIモデルを推論する

# ailia SDKを使用してFlutterでONNX形式のAIモデルを推論する

[![Kazuki Kyakuno](../images/ailia-sdk_____flutter_onnx___ai_______-7c68509b296/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--7c68509b296---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--7c68509b296---------------------------------------)

17 min read

·

Jul 31, 2023

--

Share

ailia SDKを使用してFlutterでONNXを推論するチュートリアルです。FFIを使用して、ailia SDKのC APIをDartに変換することで、簡単にONNX形式のAIモデルを推論可能です。

## Flutterについて

FlutterはGoogleが開発しているクロスプラットフォームの開発環境です。プログラミング言語としてはDartを採用しており、Windows、macOS、iOS、Android、Web向けのGUIアプリを開発可能です。

Press enter or click to view image in full size

![]()

<https://flutter.dev/>

## Dartについて

DartはGoogleが開発しているプログラミング言語です。CとC#とJavaScriptが合わさったような言語仕様となっています。

Press enter or click to view image in full size

![]()

<https://dart.dev/>

## ailia SDKについて

ailia SDKはaxが開発しているクロスプラットフォームのAI推論エンジンです。C、C++、C#、Python、JNIを使用してONNX形式のAIモデルを推論可能です。開発したアプリは、Windows、macOS、iOS、Android、Linux、RaspberryPi、Jetsonで動作します。評価版は下記からダウンロード可能です。

[## ax Inc.

### ax株式会社のコーポレートサイトです。あらゆるデバイスにAI が載る未来。そのような未来が来ることを我々は信じています。その未来に向けて我々は高速なSDK を開発し、最新のAI モデルを常に研究し続けます。ax 株式会社は最新のAI…

axinc.jp](https://axinc.jp/trial/?source=post_page-----7c68509b296---------------------------------------)

## FFIを使用してailia.hをailia.dartに変換する

Flutterからailia SDKを使用するには、DartのFFIを使用して、ailia SDKのC APIをDartから呼び出し可能に変換します。FFI（Foreign Function Interface）はDartからNativeのAPIを呼び出すインタフェースです。変換には、DartのPackageであるffigenを使用します。

下記の作業はailiaのDartファイルを生成するために必要です。弊社の提供している、変換済みのDartファイルを使用する場合は作業不要です。

ffigenの使用にはllvmが必要なため、macOSの場合はbrewでllvmをインストールしています。llvmの最新版はllvm@16ですが、M1 macの場合はインストールに失敗するため、llvm@15を使用しました。

```
brew install llvm@15
```

brewのllvmがx86\_64の場合はFlutterもx86\_64を、brewのllvmがarm64の場合はFlutterもarm64を使用する必要があります。

llvmをインストールした後、[pubspec.yaml](https://github.com/axinc-ai/ailia-flutter/blob/main/pubspec.yaml)にffigenを追加し、下記のコマンドで.hを.dartに変換します。

```
dart run ffigen --config ffigen_ailia.yaml
```

[ffigen\_ailia.yaml](https://github.com/axinc-ai/ailia-flutter/blob/main/ffigen_ailia.yaml)は下記のように記述します。変換元のヘッダファイルのパスと、変換先のDartファイルのパスを設定します。

```
name: 'ailiaFFI'  
description: 'Written for the FFI article'  
output: 'lib/ffi/ailia.dart'  
headers:  
  entry-points:  
    - 'native/ailia.h'  
    - 'native/ailia_classifier.h'  
    - 'native/ailia_detector.h'  
    - 'native/ailia_feature_extractor.h'  
    - 'native/ailia_format.h'  
    - 'native/ailia_pose_estimator.h'  
llvm-path:  
  - '/usr/local/opt/llvm@15'
```

生成したインタフェースは[lib/ffi/ailia.dart](https://github.com/axinc-ai/ailia-flutter/blob/main/lib/ffi/ailia.dart)に出力されます。

なお、Dartでは\_で始まる関数はPrivate関数になります。そのため、\_で始まるailiaの構造体は変換後にfinalが付与されず、コンパイルエラーになります。エラーが出た構造体については、手動でfinalを付与してください。

## DLLをプロジェクトに登録する

DartからはDynamicLibraryクラスを使用してailiaを読み込むため、ailia SDKの評価版をダウンロードし、libraryフォルダのライブラリをFlutterのプロジェクトに組み込みます。

### macOS

macOSの場合は、macosフォルダにlibailia.dylibを登録した後、macos/Runner.xcworkspaceを開き、下記の手順に沿ってlibalia.dylibを登録します。

Press enter or click to view image in full size

![]()

macOSのライブラリの登録（<https://docs.flutter.dev/platform-integration/macos/c-interop>）

具体的に、libailia.dylibをRunner/Frameworksに追加し、Embed & Signに設定します。また、ライブラリのフォルダパスをBuild SettingsのLibrary Search Pathsに追加します。

Press enter or click to view image in full size

![]()

Frameworkへの登録

Press enter or click to view image in full size

![]()

SearchPathの設定

この操作は、macOSフォルダのailia.podspecに下記を追加することで自動化が可能です。

```
  s.source_files     = 'Classes/**/*'  
  s.vendored_libraries = '*.dylib'
```

### iOS

iOSの場合は、libailia.aをiosフォルダに配置した後、ios/Runner.xcworkspaceを開き、libailia.aとlibc++.tbd、Accelerate.framework、MetalPerformanceShaderをFrameworksに追加します。

Press enter or click to view image in full size

![]()

iOSのライブラリの登録

この操作は、iOS/ailia.podspecに下記を追加することで自動化が可能です。iOSの場合、s.librariesに.aのlibを除いた名前を記載しないと、.aがリンクされず、実行時のシンボル読み込みでエラーになります。

```
  s.source_files = 'Classes/**/*'  
  s.vendored_libraries = '*.a'  
  s.libraries = "ailia"  
  s.framework = ["Accelerate", "MetalPerformanceShaders"]
```

加えて、iOSの場合は、libailia.aの中の関数を一度も呼び出していないと、リンカでリンクされず、dlopenでSymbol not foundのエラーになります。そこで、[ailia\_link.c](https://github.com/axinc-ai/ailia-flutter/blob/main/ios/Runner/ailia_link.c)を追加し、ダミーでailiaGetVersion()を呼び出しておきます。

### Android

Androidの場合は、android/app/src/jniLibsの中にライブラリをコピーします。

![]()

Androidのライブラリの登録

### Windows

Windowsの場合は、ビルド後に、build/windows/runner/Debugにailia.dllをコピーします。

![]()

Windowsのライブラリの登録

この操作は、windows/CmakeList.txtのailia\_bundled\_librariesにDLL名を記載することで自動化可能です。DLL名にワイルドカードは使用できません。また、DLLをフルパスで指定しないとビルドエラーになるため、${CMAKE\_CURRENT\_SOURCE\_DIR}を使用します。

```
set(ailia_bundled_libraries  
  "${CMAKE_CURRENT_SOURCE_DIR}/x64/ailia.dll"  
  PARENT_SCOPE  
)
```

### モデルファイルの配置

モデルファイルはassetsフォルダに配置し、[pubspec.yaml](https://github.com/axinc-ai/ailia-flutter/blob/main/pubspec.yaml)でアプリに含むようにします。

```
  assets:  
    - assets/resnet18.onnx  
    - assets/clock.jpg
```

assetsは1ファイルにパックされるため、ailia SDKから使用する場合は、TemporaryDirectoryにコピーした後に使用します。

```
  Future<File> copyFileFromAssets(String path) async {  
    final byteData = await rootBundle.load('assets/$path');  
    final buffer = byteData.buffer;  
    Directory tempDir = await getTemporaryDirectory();  
    String tempPath = tempDir.path;  
    var filePath =  
      tempPath + '/${path}';  
    return File(filePath)  
      .writeAsBytes(buffer.asUint8List(byteData.offsetInBytes,   
    byteData.lengthInBytes));  
  }
```

## 推論コード

推論コードは[lib/ailia\_predict\_sample.dart](https://github.com/axinc-ai/ailia-flutter/blob/main/lib/ailia_predict_sample.dart)にあります。C APIをそのまま呼び出し可能です。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

DLLはDynamicLibraryインタフェースで読み込みます。iOSの場合はStatic Link Libraryを使用するため、processを使用します。

```
DynamicLibrary ailiaGetLibrary(){  
    final DynamicLibrary library;  
    if (Platform.isIOS){  
      library = DynamicLibrary.process();  
    }else{  
      library = DynamicLibrary.open(_getPath());  
    }  
    return library;  
}
```

C APIのポインタはPointerタイプで接続します。

```
void ailiaEnvironmentSample(){  
    final ailia = ailia_dart.ailiaFFI(ailiaGetLibrary());  
    final Pointer<Uint32> count = malloc<Uint32>();  
    count.value = 0;  
    ailia.ailiaGetEnvironmentCount(count);  
    print("Environment ${count.value}");  
    malloc.free(count);  
}
```

構造体は、.refでメンバ参照可能です。

```
Pointer<Pointer<ailia_dart.AILIAEnvironment>> pp_env = malloc<Pointer<ailia_dart.AILIAEnvironment>>();  
ailia.ailiaGetEnvironment(pp_env, env_idx, ailia_dart.AILIA_ENVIRONMENT_VERSION);  
Pointer<ailia_dart.AILIAEnvironment> p_env = pp_env.value;  
print("Backend ${p_env.ref.backend}");  
print("Name ${p_env.ref.name.cast<Utf8>().toDartString()}");  
malloc.free(pp_env);
```

推論では、Floatのバッファを確保して入力データを書き込み、ailiaPredictを呼び出すことで推論結果を得ることが可能です。

```
  Pointer<Float> dest = malloc<Float>(1000);  
  Pointer<Float> src = malloc<Float>(image_size * image_size * image_channels);  
  
  List pixel = data.buffer.asUint8List().toList();  
  
  List mean = [0.485, 0.456, 0.406];  
  List std = [0.229, 0.224, 0.225];  
  
  for (int y = 0; y < image_size; y++){  
    for (int x = 0; x < image_size; x++){  
      for (int rgb = 0; rgb < 3; rgb++){  
        src[y * image_size + x + rgb * image_size * image_size] = (pixel[(image_size * y + x) * 4 + rgb] / 255.0 - mean[rgb])/std[rgb];  
      }  
    }  
  }  
  
  int sizeof_float = 4;  
  status = ailia.ailiaPredict(pp_ailia.value, dest.cast<Void>(), sizeof_float * num_class, src.cast<Void>(), sizeof_float * image_size * image_size * image_channels);  
  
  double max_prob = 0.0;  
  int max_i = 0;  
  for (int i = 0; i < num_class; i++){  
    if (max_prob < dest[i]){  
      max_prob = dest[i];  
      max_i = i;  
    }  
  }  
  
  malloc.free(dest);  
  malloc.free(src);
```

## Flutterからailia SDKを使用するサンプルプロジェクト

下記にFlutterからailia SDKを使用するサンプルプロジェクトをアップロードしています。

[## GitHub - axinc-ai/ailia-flutter: Example use ailia SDK on Flutter

### Example use ailia SDK on Flutter. Contribute to axinc-ai/ailia-flutter development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-flutter?source=post_page-----7c68509b296---------------------------------------)

サンプルを実行し、右下のボタンを押すと、resnet18で推論し、推論結果を得ることができます。

Press enter or click to view image in full size

![]()

Flutterのサンプルの実行例

## ailia SDKのAPIについて

Flutterからはailia SDKの全てのC APIを呼び出し可能です。

ailia SDKのC APIのリファレンスは下記を参照してください。

[## ailia: ailia SDK Document

### ailiaは、マルチプラットフォームに対応したDNN（Deep Neural Network、畳み込みニューラルネットワーク）の高速推論エンジンです。…

axinc-ai.github.io](https://axinc-ai.github.io/ailia-sdk/api/cpp/jp/?source=post_page-----7c68509b296---------------------------------------)

ailia SDKのC APIの使用例のサンプルは下記を参照してください。

[## GitHub — axinc-ai/ailia-models-cpp: C++ version of ailia models repository

### C++ version of ailia models repository. Contribute to axinc-ai/ailia-models-cpp development by creating an account on…

github.com](https://github.com/axinc-ai/ailia-models-cpp?source=post_page-----7c68509b296---------------------------------------)

ailia SDKを使用して複数の入出力を持つモデルを推論する場合の実装例は下記を参照してください。

[## ailia SDK API解説(Predict API)

### ailia SDKのコアAPIであるPredict APIのチュートリアルです。Predict APIはテンソルを入力してテンソルを出力する最も基本的なAPIとなります。

medium.com](https://medium.com/axinc/ailia-sdk-api%E8%A7%A3%E8%AA%AC-predict-api-dcae1dc62780?source=post_page-----7c68509b296---------------------------------------)

## プラグインを作成する

上記の流れは、アプリケーションにライブラリを直接、組み込みましたが、プラグインを新規作成し、プラグインの方にライブラリを組み込むことも可能です。アプリケーションからはプラグイン経由でライブラリを使用します。

プラグインのためのプロジェクトの作成は、下記のコマンドを使用します。

```
flutter create --template=plugin --platform=android,ios,linux,windows,macos ailia
```

プラグインでは、ルートフォルダにライブラリを、exampleフォルダにサンプルを格納します。プラグインの場合、iOSのリンクエラー対策に、[ios/Classes/AIliaPluginPreventStrip.c](https://github.com/axinc-ai/ailia-sdk-flutter/blob/main/ios/Classes/AiliaPluginPreventStrip.c)を作成し、.aの中の関数をダミーで呼び出しています。

プラグイン形式のailia SDKは下記に公開しています。

[## GitHub - axinc-ai/ailia-sdk-flutter: Flutter binding for ailia SDK

### Flutter binding for ailia SDK. Contribute to axinc-ai/ailia-sdk-flutter development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-sdk-flutter?source=post_page-----7c68509b296---------------------------------------)

このプラグインを使用することで、pubspecを使用し、より簡単にailia SDKをアプリケーションに取り込むことが可能です。

[## ailia SDKがFlutterのpubspecからインストール可能に

### ailia SDKがFlutterのpubspecを使用したインストールに対応しました。これにより、Flutterのアプリケーションに簡単にailia SDKを取り込み可能です。

medium.com](https://medium.com/axinc/ailia-sdk%E3%81%8Cflutter%E3%81%AEpubspec%E3%81%8B%E3%82%89%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E5%8F%AF%E8%83%BD%E3%81%AB-f008229f7862?source=post_page-----7c68509b296---------------------------------------)

## トラブルシューティング

### Xcodeのビルドに失敗する

下記のコマンドでプロジェクトをクリーンし、再度、ビルドしてください。

```
flutter clean  
flutter pub get
```

### ailiaCreate failed -20が発生する

ailia SDKの評価版を使用している場合にライセンスファイルが存在しない場合に発生します。

macOSの場合はライセンスファイルを~/Library/SHALO/に配置しているか、Windowsの場合はライセンスファイルをailia.dllと同じ場所に配置しているか確認してください。

また、ライセンスファイルを読み込むため、macOSの評価版の場合はDebugProfile.entitlementsのcom.apple.security.app-sandboxを無効にする必要があります。macOSの製品版では、app-sandboxを有効にした開発も可能です。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。