---
title: "CrnnSoundClassification : 音声を分類する機械学習モデル"
author: "Kazuki Kyakuno"
date: 2021-02-03
original_url: https://tech.ailia.ai/crnnsoundclassification-音声を分類する機械学習モデル-2a35564dad42
---

# CrnnSoundClassification : 音声を分類する機械学習モデル

# CrnnSoundClassification : 音声を分類する機械学習モデル

[![Kazuki Kyakuno](../images/crnnsoundclassification-______________-2a35564dad42/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--2a35564dad42---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--2a35564dad42---------------------------------------)

7 min read

·

Dec 11, 2020

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「CrnnSoundClassification」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## CrnnSoundClassificationの概要

CrnnSoundClassificationは音声ファイルを入力として、10クラスに分類する機械学習モデルです。

Press enter or click to view image in full size

![]()

出典：<https://github.com/ksanjeevan/crnn-audio-classification>

認識できるクラスは下記となります。

> air\_conditioner, car\_horn, children\_playing, dog\_bark, drilling, enginge\_idling, gun\_shot, jackhammer, siren, and street\_music

[## ksanjeevan/crnn-audio-classification

### UrbanSound classification using Convolutional Recurrent Networks in PyTorch - ksanjeevan/crnn-audio-classification

github.com](https://github.com/ksanjeevan/crnn-audio-classification?source=post_page-----2a35564dad42---------------------------------------)

## CrnnSoundClassificationのアーキテクチャ

CrnnSoundClassificationでは、入力音声に対してMelspectrogram変換を行なってスペクトルに変換した後、CNNとLSTMを使用してFeatureを取得、FCとSoftmaxでクラス分類を行います。

Press enter or click to view image in full size

![]()

出典：<https://github.com/ksanjeevan/crnn-audio-classification>

スペクトル変換のパラメータはnet/model.pyで定義されています。

> self.spec = MelspectrogramStretch(hop\_length=None, num\_mels=128, fft\_length=2048, norm=’whiten’, stretch\_param=[0.4, 0.4])

入力サイズは可変長で、(1,2,num\_seconds \* sample\_rate)が入力となります。例えば、(66026, 2)のwavファイルが入力された場合、AudioInference.inferで(1,66026,1)に変換されます。これをスペクトル変換し、(1,1,128,65)がConvへの入力となります。(99225, 2)のwavファイルが入力された場合、(1,1,128,97)がConvへの入力となります。

Convでは3x3のmaxpoolが1回と、4x4のmaxpoolが2回実行されるため、横幅が(128,65)だとGiven input size: (64x8x2). Calculated output size: (64x2x0). Output size is too smallのエラーが発生します。そのため、短いサンプルはパディングを行う必要があります。

CrnnSoundClassificationはUrbanSound8Kデータセットを使用して学習されています。UrbanSound8Kデータセットはfreesound.orgのfield recordingから収集されています。

[## UrbanSound8K

### This dataset contains 8732 labeled sound excerpts (<=4s) of urban sounds from 10 classes: air\_conditioner, car\_horn…

urbansounddataset.weebly.com](https://urbansounddataset.weebly.com/urbansound8k.html?source=post_page-----2a35564dad42---------------------------------------)

## CrnnSoundClassificationのPytorchでの推論

Pytorchで推論するには、下記のIssueから学習済みモデルを入手します。

[## Model · Issue #2 · ksanjeevan/crnn-audio-classification

### You can't perform that action at this time. You signed in with another tab or window. You signed out in another tab or…

github.com](https://github.com/ksanjeevan/crnn-audio-classification/issues/2?source=post_page-----2a35564dad42---------------------------------------)

config.jsonが学習時の設定、model.cfgがモデルアーキテクチャ、model\_best.pthが重みになっています。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

推論を行うには下記のコマンドを使用します。

> python3 run.py dog.wav -r downloaded\_model/model\_best.pth

デフォルトでは、run.pyの168行目で、pthに含まれるフルパスからmodel.cfgが読み込まれます。学習したPCとは異なる環境で推論したい場合は、args.resumeの中のconfig = checkpoint[‘config’]のあとで、下記のようにmodel.cfgへのパスを書き換える必要があります。

> config[“cfg”] = “./downloaded\_model/model.cfg”

内部的には、torchparseを使用して、model.cfgからネットワークが構築されます。このパスが間違っている場合、下記のエラーが発生します。

> File “/crnn-audio-classification/net/model.py”, line 55, in forward  
>  xt = [self.net](http://self.net/)[‘convs’](xt)  
> KeyError: ‘convs’

## CrnnSoundClassificationの再学習

UrbanSound8Kと同様のcsvファイルを作成することで、独自のデータセットで再学習することが可能です。

> ./run.py train -c config.json — cfg arch.cfg

データセットのレイアウトは下記のようになっています。

> UrbanSound8K/audio/fold1/\*.wav  
> UrbanSound8K/audio/fold2/\*.wav  
> UrbanSound8K/metadata/UrbanSound8K.csv

csvのフォーマットは下記にようになっています。

> slice\_file\_name , fsID , start , end , salience , fold , classID , class  
> 100032–3–0–0.wav , 100032 , 0.0 , 0.317551 , 1 , 5 , 3 , dog\_bark

## CrnnSoundClassificationの使用方法

ailia SDKで使用するには下記のコマンドを使用します。任意の音声ファイルを分類することができます。

> python3 crnn\_sound\_classification.py -i dog.wav

この例では、dog.wavがdog\_barkに分類されます。

> dog\_bark  
> 0.8683825731277466

[## axinc-ai/ailia-models

### Pretrained models for ailia SDK. Contribute to axinc-ai/ailia-models development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/crnn_audio_classification?source=post_page-----2a35564dad42---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。