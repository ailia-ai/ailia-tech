---
title: "Pytorchで学習したAIモデルをiOSとAndroidに実装する"
author: "Kazuki Kyakuno"
date: 2023-06-30
original_url: https://tech.ailia.ai/pytorchで学習したaiモデルをiosとandroidに実装する-307d1871bc14
---

# Pytorchで学習したAIモデルをiOSとAndroidに実装する

# Pytorchで学習したAIモデルをiOSとAndroidに実装する

[![Kazuki Kyakuno](../images/pytorch_____ai____ios_android_____-307d1871bc14/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--307d1871bc14---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--307d1871bc14---------------------------------------)

11 min read

·

Jun 30, 2023

--

Share

Pytorchで学習したAIモデルをailia SDKを使用してiOSとAndroidに実装する方法を解説します。

## AIモデルのエッジ実装の課題

Pytorchを使用してPC上で動くAIモデルが完成した後、そのAIモデルをiOSやAndroidなどにエッジ実装することを考えます。

Press enter or click to view image in full size

![]()

Pytorch to iOS/Android

その場合、次のような課題があり、 ailia SDKを使用することで解決可能です。

### プラットフォームごとに別々のフレームワークを使用する必要がある

iOSではCoreML、AndroidではTensorFlowLiteを使用する必要があります。プラットフォームごとに異なるAPIを使用する必要があり、それぞれに最適化が必要です。

ailia SDKを使用すると、Windows、macOS、Linux、iOS、Androidで共通のAPIで推論を実行可能です。

### プラットフォームごとに異なる言語を使用する必要がある

iOSではObjectiveCやSwift、AndroidではJavaやKotlinを使用する必要があります。

ailia SDKはゲームエンジンのUnityに対応しているため、C#で統一して開発可能です。

### モデルの変換エラーが発生する

Pytorchから異なるフレームワークに移植する際、モデルの変換エラーが発生することがあります。近年のAIモデルは複雑化が進んでおり、特に、5次元テンソルを使用する場合や、フレーム間でTensorのShapeが動的に変化するようなケースで問題が発生しやすいです。

ailia SDKでは、モデル変換不要で、共通のONNXモデルをPCとスマートフォンで使用可能です。そのため、PC上で動作が確認できれば、そのまま、iOSとAndroidで実行することが保証され、モデルの変換エラーに悩まされることがありません。

### GPUが使用できない

TensorFlowLiteのGPU delegateは使用できるレイヤーが少ないため、結果として、AndroidでGPUが使用できませんでした。

ailia SDKでは、AndroidではVulkanでGPUが使用可能です。もちろん、iOSではCoreMLと同様にMetalが使用可能です。

## ailia SDKを使用した開発の流れ

### 開発の流れ

ailia SDKを使用した開発では、PytorchのモデルをONNXに変換した後、ONNXをPython上で読み込んで推論、動作確認後にUnityとC#でアプリを開発、エッジデバイスで実行します。

Press enter or click to view image in full size

![]()

ailia SDKの開発のワークフロー

### PytorchのモデルをONNXに変換する

ailia SDKはONNXを使用しているため、まず、PytorchのモデルをONNXに変換します。PytorchからONNXを出力するには、torch.onnx.exportを使用します。

入力が固定Shapeの場合、Torchのモデルを示すmodelと、入力テンソルを示すxを引数にexportを呼び出すことで、ONNXを出力可能です。

```
torch.onnx.export(model, x, 'output.onnx', verbose=False, opset_version=11)
```

入力の形状を動的に指定したい場合は、dynamic\_axesを使用します。この例では、x1とx2の2変数を入力とし、x1のaxis0とaxis3を変数として、可変にしています。

```
torch.onnx.export(model, (x1, x2), 'output.onnx', verbose=False, opset_version=11, input_names=["input1", "input2"], dynamic_axes={"input1": {0: "batch_size", 3:"samples"}})
```

### ONNXを読み込んで推論する

エクスポートしたONNXは、ONNX Runtimeやailia SDKを使用して動作確認します。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

ONNX Runtimeを使用する方法です。

```
import onnxruntime  
model = onnxruntime.InferenceSession("input.onnx")  
output = model.run(None, {"input1":tensor.numpy()})[0]  
output = torch.from_numpy(output.astype(np.float32)).clone()
```

ailia SDKを使用する方法です。

```
import ailia  
model = ailia.Net(None, "input.onnx")  
output = model.run({"input1":tensor.numpy()})[0]  
output = torch.from_numpy(output.astype(np.float32)).clone()
```

ailia SDKは下記からダウンロード可能です。

[## ax Inc.

### ax株式会社のコーポレートサイトです。あらゆるデバイスにAI が載る未来。そのような未来が来ることを我々は信じています。その未来に向けて我々は高速なSDK を開発し、最新のAI モデルを常に研究し続けます。ax 株式会社は最新のAI…

axinc.jp](https://axinc.jp/trial/?source=post_page-----307d1871bc14---------------------------------------)

Python環境にインストールするには、ダウンロードしたSDKで下記のコマンドを実行します。

```
cd ailia_sdk/python  
python3 bootstrap.py  
pip3 install .
```

動作検証で問題なければ、デバイス実装に移ります。

### Unityから推論する

Unityにailia SDKのUnity Packageをインポートします。変換したONNXファイルを、StreamingAsstesフォルダに配置します。推論のコード例は下記のようになります。モデルを開き、テンソルを与えると、テンソルが出力されます。

```
float [] infer(float [] input1){  
    // Open model file  
    AiliaModel model=new AiliaModel();  
#if UNITY_ANDROID  
    model.OpenFile(null,Application.temporaryCachePath+"/input.onnx");  
#else  
    model.OpenFile(null,Application.streamingAssetsPath+"/input.onnx");  
#endif  
  
    // Set input  
    Ailia.AILIAShape shape=new Ailia.AILIAShape();  
    shape.x=input1.Length;  
    shape.y=1;  
    shape.z=1;  
    shape.w=1;  
    shape.dim=4;  
    model.SetInputBlobShape(shape, model.FindBlobIndexByName("input1"));  
    model.SetInputBlobData(input1, model.FindBlobIndexByName("input1"));  
  
    // Infer  
    model.Update();  
  
    // Get output  
    Ailia.AILIAShape output_shape=model.GetOutputShape();  
    float [] output=new float[output_shape.x * output_shape.y * output_shape.z * output_shape.w];  
    model.GetBlobData(output,(int)model.GetOutputBlobList()[0]);  
    model.Close();  
    return output;  
}
```

Androidの場合、StreamingAssetsのファイルは直接アクセスできないため、temporaryCachePathにコピーします。

```
private void CopyModelToTemporaryCachePath (string file_name)  
{  
#if UNITY_ANDROID && !UNITY_EDITOR  
    string prefix="";  
#else  
    string prefix="file://";  
#endif  
  
    string path = prefix+Application.streamingAssetsPath + "/" + file_name;  
    string toPath = Application.temporaryCachePath + "/" + file_name;  
  
    Debug.Log("Copy "+path+" to "+toPath);  
  
    if (System.IO.File.Exists(toPath) == true)  
    {  
        FileInfo fileInfo = new System.IO.FileInfo(toPath);  
        if (fileInfo.Length != 0)  
        {  
            Debug.Log("Already exists : " + toPath + " " + fileInfo.Length);  
            return;  
        }  
    }  
  
    WWW www = new WWW(path);  
    while (!www.isDone)  
    {  
        // NOP.  
    }  
    File.WriteAllBytes(toPath, www.bytes);  
}
```

### デバイスで動作を確認する

Unityで書いたプログラムは、iOSとAndroidにそのままデプロイして実行可能です。

## ailia SDKのSupplemental Library

### Supplemental Libraryの概要

Pytorchの推論は以上の手順でailia SDKで実装可能です。しかし、実際のアプリ開発では、torch\_audioを使用していたり、transformersのtokenizerを使用したりしている場合があります。これらのライブラリはPythonからしか使用できないため、デバイス実装が行えません。

これらの問題を解決するため、ailia SDKではSupplemental Libraryを提供しています。

### ailia.audio

torch\_audioやlibrosaに相当するライブラリです。音声のMelSpectrum変換などに対応しています。

[## GitHub - axinc-ai/ailia-audio-samples: ailia.audio samples of unity

### ailia.audio samples of unity. Contribute to axinc-ai/ailia-audio-samples development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-audio-samples?source=post_page-----307d1871bc14---------------------------------------)

### ailia.tokenizer

transformersのtokenizerに相当するライブラリです。テキストを日本語BERTのトークンに変換することなどが可能です。

[## ailia Tokenizer : UnityやC++から使用できるNLP向けトークナイザ

### UnityやC++から使用できるNLP向けトークナイザのailia Tokenizerのご紹介です。ailia Tokenizerを使用することで、Python不要で、NLPのトークナイズを行うことが可能です。

medium.com](https://medium.com/axinc/ailia-tokenizer-unity%E3%82%84c-%E3%81%8B%E3%82%89%E4%BD%BF%E7%94%A8%E3%81%A7%E3%81%8D%E3%82%8Bnlp%E5%90%91%E3%81%91%E3%83%88%E3%83%BC%E3%82%AF%E3%83%8A%E3%82%A4%E3%82%B6-b60b68c46b06?source=post_page-----307d1871bc14---------------------------------------)

## まとめ

ailia SDKを使用することで、Pytorchで学習したモデルを簡単にエッジデバイスに実装することが可能です。ぜひ、ご活用ください。

また、ax株式会社では、お客様のAIモデルをデバイス実装する開発サービスもご提供しています。お気軽にお問い合わせください。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。