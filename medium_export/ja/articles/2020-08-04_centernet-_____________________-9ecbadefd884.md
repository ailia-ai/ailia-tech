---
title: "CenterNet : アンカーレスな物体検出を行う機械学習モデル"
author: "Kazuki Kyakuno"
date: 2020-08-04
lastmod: 2020-10-20
original_url: https://tech.ailia.ai/centernet-アンカーレスな物体検出を行う機械学習モデル-9ecbadefd884
tags: [ailia-models]
---

# CenterNet : アンカーレスな物体検出を行う機械学習モデル

# CenterNet : アンカーレスな物体検出を行う機械学習モデル

[![Kazuki Kyakuno](../images/centernet-_____________________-9ecbadefd884/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--9ecbadefd884---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--9ecbadefd884---------------------------------------)

Aug 4, 2020

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「CenterNet」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## CenterNetの概要

CenterNetはアンカーレスな物体検出を行う機械学習モデルです。2019年4月に公開されました。

[## Objects as Points

### Detection identifies objects as axis-aligned boxes in an image. Most successful object detectors enumerate a nearly…

arxiv.org](https://arxiv.org/abs/1904.07850?source=post_page-----9ecbadefd884---------------------------------------)

CenterNetを使用することで、COCOの80カテゴリのバウンディングボックスを計算することができます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

CenterNetでは、OpenPoseなどのヒートマップベースの手法を物体検出に導入することで、YOLOv2以降で使用されているアンカーを使用せずに物体検出を行うことができます。

## アンカーについて

アンカーは、予め決まられたバウンディングボックスで、k個のアスペクト比の異なるボックスで定義されます。各バウンディングボックスごとに物体検出を行うことで、同時に検出できるオブジェクト数を増加させることができます。YOLOv2から導入されています。

Press enter or click to view image in full size

![](../images/centernet-_____________________-9ecbadefd884/image_001.png)

（出典：<https://arxiv.org/abs/1904.07850>）

## CenterNetのアーキテクチャ

CenterNetでは、物体の中心座標のヒートマップと、中心座標のオフセット、物体のサイズを推論します。

Press enter or click to view image in full size

![](../images/centernet-_____________________-9ecbadefd884/image_002.png)

（出典：<https://arxiv.org/abs/1904.07850>）

## CenterNetの性能

CenterNetはYOLOv3やRetinaNetよりも高精度な推論が可能です。

Press enter or click to view image in full size

![](../images/centernet-_____________________-9ecbadefd884/image_003.png)

（出典：<https://arxiv.org/abs/1904.07850>）

## ailia SDKでの利用

ailia SDKでは下記のサンプルでCenterNetを実行することができます。

[## axinc-ai/ailia-models

### Shape : (1, 3, 512, 512) Range : [0.0, 1.0] category : [0,79] probablity : [0.0,1.0] position : x, y, w, h [0,1]…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_detection/centernet?source=post_page-----9ecbadefd884---------------------------------------)

下記のコマンドでWEBカメラから物体を検出します。

> python3 centernet.py -v 0

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。