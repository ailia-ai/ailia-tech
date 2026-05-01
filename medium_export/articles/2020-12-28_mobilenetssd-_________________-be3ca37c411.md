---
title: "MobilenetSSD : 高速に物体検出を行う機械学習モデル"
author: "Kazuki Kyakuno"
date: 2020-12-28
original_url: https://tech.ailia.ai/mobilenetssd-高速に物体検出を行う機械学習モデル-be3ca37c411
tags: [ailia-model]
---

# MobilenetSSD : 高速に物体検出を行う機械学習モデル

# MobilenetSSD : 高速に物体検出を行う機械学習モデル

[![Kazuki Kyakuno](../images/mobilenetssd-_________________-be3ca37c411/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--be3ca37c411---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--be3ca37c411---------------------------------------)

10 min read

·

Sep 23, 2020

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「MobilenetSSD」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## MobilenetSSDの概要

MobilenetSSDは入力された画像から物体のバウンディングボックスとカテゴリを計算するEndToEndの物体検出モデルです。SingleShotDetectorの物体検出のbackboneをMobilenetとすることで、モバイル向けに最適化された高速な物体検出を実現します。

[## SSD: Single Shot MultiBox Detector

### We present a method for detecting objects in images using a single deep neural network. Our approach, named SSD…

arxiv.org](https://arxiv.org/abs/1512.02325?source=post_page-----be3ca37c411---------------------------------------)

[## MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications

### We present a class of efficient models called MobileNets for mobile and embedded vision applications. MobileNets are…

arxiv.org](https://arxiv.org/abs/1704.04861?source=post_page-----be3ca37c411---------------------------------------)

## MobilenetSSDのアーキテクチャ

MobilenetSSDは(3,300,300)の画像を入力として、(1,3000,4)のboxesと(1,3000,21)のscoresを出力します。boxesには(cx,cy,w,h)がデフォルトボックスとの差分値として記載されています。scoresにはVOCの20カテゴリのscoreが記載されています。scoresのうちcat=0はBACKGROUNDとして予約されています。

Press enter or click to view image in full size

![](../images/mobilenetssd-_________________-be3ca37c411/image_001.png)

出典：<https://arxiv.org/pdf/1512.02325.pdf>

SSDでは、任意のbackboneでFeatureを抽出した後、Extra Feature Layersで解像度を落としながら、各解像度でバウンディングボックスを計算します。MobilenetSSDでは、6段階の解像度の出力をConcatして、合計で3000のバウンディングボックスを計算します。最後に、NMSで重複除外します。

Press enter or click to view image in full size

![](../images/mobilenetssd-_________________-be3ca37c411/image_002.png)

出典：<https://arxiv.org/pdf/1512.02325.pdf>

MobilenetSSDのConfigは下記になります。SSDSpecに、各解像度ごとのデフォルトボックスが定義されます。

> image\_size = 300  
> image\_mean = np.array([127, 127, 127]) # RGB layout  
> image\_std = 128.0  
> iou\_threshold = 0.45  
> center\_variance = 0.1  
> size\_variance = 0.2
>
> specs = [  
>  SSDSpec(19, 16, SSDBoxSizes(60, 105), [2, 3]),  
>  SSDSpec(10, 32, SSDBoxSizes(105, 150), [2, 3]),  
>  SSDSpec(5, 64, SSDBoxSizes(150, 195), [2, 3]),  
>  SSDSpec(3, 100, SSDBoxSizes(195, 240), [2, 3]),  
>  SSDSpec(2, 150, SSDBoxSizes(240, 285), [2, 3]),  
>  SSDSpec(1, 300, SSDBoxSizes(285, 330), [2, 3])  
> ]

[## qfgaohao/pytorch-ssd

### MobileNetV1, MobileNetV2, VGG based SSD/SSD-lite implementation in Pytorch 1.0 / Pytorch 0.4. Out-of-box support for…

github.com](https://github.com/qfgaohao/pytorch-ssd/blob/master/vision/ssd/config/mobilenetv1_ssd_config.py?source=post_page-----be3ca37c411---------------------------------------)

SSDSpecは下記で定義されます。

> SSDSpec = collections.namedtuple(‘SSDSpec’, [‘feature\_map\_size’, ‘shrinkage’, ‘box\_sizes’, ‘aspect\_ratios’])

SSDSpec(19, 16, SSDBoxSizes(60, 105), [2, 3])の場合、60x60と105x105のサイズのボックスと、アスペクト2の120x60、60x120、210x105、105x210の6つのボックスが定義されます。

[## qfgaohao/pytorch-ssd

### You can't perform that action at this time. You signed in with another tab or window. You signed out in another tab or…

github.com](https://github.com/qfgaohao/pytorch-ssd/blob/master/vision/utils/box_utils.py?source=post_page-----be3ca37c411---------------------------------------)

6段階の認識結果がConcatされ、合計で3000のバウンディングボックスが生成されます。

## ailia SDKからMobilenetSSDを使用する

ailia SDKで使用するサンプルは下記になります。

[## axinc-ai/ailia-models

### Ailia input shape(1, 3, 300, 300) Range:[0, 1] Automatically downloads the onnx and prototxt files on the first run. It…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_detection/mobilenet_ssd?source=post_page-----be3ca37c411---------------------------------------)

下記のコマンドでWEBカメラに対してMobilenetSSDを実行可能です。

> python3 mobilenet\_ssd.py -v 0

## MobilenetSSDを独自にデータセットで学習する

MobilenetSSDを使用して学習を行うには下記のpytorch-ssdを使用します。

[## qfgaohao/pytorch-ssd

### This repo implements SSD (Single Shot MultiBox Detector). The implementation is heavily influenced by the projects…

github.com](https://github.com/qfgaohao/pytorch-ssd?source=post_page-----be3ca37c411---------------------------------------)

pytorch-ssdではDataLoaderにLambdaを使用しているため、Windowsでは学習できません。LinuxもしくはMacを使用する必要があります。

[## Can't pickle local object 'DataLoader.\_\_init\_\_. . '

### Hi all, I hope everybody reading this is having a great day. So I have a problem with torchvision.transforms.Lambda()…

discuss.pytorch.org](https://discuss.pytorch.org/t/cant-pickle-local-object-dataloader-init-locals-lambda/31857/8?source=post_page-----be3ca37c411---------------------------------------)

学習データのフォーマットはopen-image-dataset formatになります。学習には下記の4つのファイルが必要です。

> /dataset/open\_images\_mixed/sub-test-annotations-bbox.csv  
> /dataset/open\_images\_mixed/sub-train-annotations-bbox.csv  
> /dataset/open\_images\_mixed/train/images.jpg  
> /dataset/open\_images\_mixed/test/images.jpg

csvのフォーマットは下記になります。

> ImageID,Source,LabelName,Confidence,XMin,XMax,YMin,YMax,IsOccluded,IsTruncated,IsGroupOf,IsDepiction,IsInside,id,ClassName

ImageIdには画像のファイル名（拡張子なし）、Xmin〜YMaxにはバウンディングボックスを0〜1で記載します。ClassNameにカテゴリを記載します。例えば、下記のように設定します。

> img\_591,xclick,/m/0gxl3,1,0.40920866666666667,0.08862621809744783,0.7894286666666666,0.6620986078886312,0,0,0,0,0,/m/0gxl3,Handgun

学習画像は、trainフォルダのImageId.jpgが参照されるため、trainフォルダに配置します。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

学習は転移学習で行うため、学習済みモデルをダウンロードします。

> wget -P models <https://storage.googleapis.com/models-hao/mb2-ssd-lite-mp-0_686.pth>

学習します。

> python3 train\_ssd.py — dataset\_type open\_images — datasets ./dataset — net mb2-ssd-lite — pretrained\_ssd models/mb2-ssd-lite-mp-0\_686.pth — scheduler cosine — lr 0.001 — t\_max 100 — validation\_epochs 5 — num\_epochs 100 — base\_net\_lr 0.001 — batch\_size 5

modelsフォルダに学習結果とopen-images-model-labels.txtが出力されます。MacBookPro13のCPUだと学習に概ね38時間かかります。

学習結果を確認します。

> python3 run\_ssd\_example.py mb2-ssd-lite models/mb2-ssd-lite-Epoch-80-Loss-2.4882763324521524.pth models/open-images-model-labels.txt input.jpg

ailia SDKではopset=10でエクスポートする必要があるため、convert\_to\_caffe2\_models.pyのtorch.onnx.exportにopset\_version=10を追加しておきます。

> torch.onnx.export(net, dummy\_input, model\_path, verbose=False, output\_names=[‘scores’, ‘boxes’], opset\_version=10)

ailia SDKで使用できるようにONNXにエクスポートします。

> python3 convert\_to\_caffe2\_models.py mb2-ssd-lite models/mb2-ssd-lite-Epoch-80-Loss-2.4882763324521524.pth models/open-images-model-labels.txt

学習からONNXへの変換まで行うサンプルは下記を参照ください。

[## axinc-ai/mobilenetssd-face

### Pytorch 1.0 Windows is not working…

github.com](https://github.com/axinc-ai/mobilenetssd-face?source=post_page-----be3ca37c411---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽にお問い合わせください。

### 参考記事

[YOLO v3 : 物体の位置と種類を検出する機械学習モデル](https://medium.com/axinc/yolov3-66c9b998c096)

[YOLO v4 : 物体を検出する機械学習モデル](https://medium.com/axinc/yolov4-%E7%89%A9%E4%BD%93%E3%82%92%E6%A4%9C%E5%87%BA%E3%81%99%E3%82%8B%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92%E3%83%A2%E3%83%87%E3%83%AB-480f0a635317)

[M2Det : 高精度な物体検出モデル](https://medium.com/axinc/m2det-%E9%AB%98%E7%B2%BE%E5%BA%A6%E3%81%AA%E7%89%A9%E4%BD%93%E6%A4%9C%E5%87%BA%E3%83%A2%E3%83%87%E3%83%AB-bf92a8a3d423)