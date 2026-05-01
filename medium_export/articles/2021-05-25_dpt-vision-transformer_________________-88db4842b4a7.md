---
title: "DPT : Vision Transformerを使用したセグメンテーションモデル"
author: "Kazuki Kyakuno"
date: 2021-05-25
original_url: https://tech.ailia.ai/dpt-vision-transformerを使用したセグメンテーションモデル-88db4842b4a7
---

# DPT : Vision Transformerを使用したセグメンテーションモデル

# DPT : Vision Transformerを使用したセグメンテーションモデル

[![Kazuki Kyakuno](../images/dpt-vision-transformer_________________-88db4842b4a7/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--88db4842b4a7---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--88db4842b4a7---------------------------------------)

May 25, 2021

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「DPT」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## DPTの概要

DPT（DensePredictionTransformers）はIntelが2021年3月に公開したTransformerを画像に適用したセグメンテーションモデルです。画像のセグメンテーションと、単眼デプス推定を行うことができます。単眼デプス推定では相対的な性能が最大で28%向上しています。セマンティックセグメンテーションではADE20Kにおいて49.02%のmIoUを達成し、SOTAとなっています。

[## Vision Transformers for Dense Prediction

### We introduce dense vision transformers, an architecture that leverages vision transformers in place of convolutional…

arxiv.org](https://arxiv.org/abs/2103.13413?source=post_page-----88db4842b4a7---------------------------------------)

## DPTのアーキテクチャ

DPTでは、Convolutional Networkの代わりに、Vision Transformerを使用します。Transformerを使用することで、Convolutional Networkに比べて、より詳細に、グローバルに一貫した予測を行うことができます。特に、大量の学習データが利用可能な場合に性能が向上します。

DPTのEncoderでは画像をタイル分割し、Embedでトークン化、Transformerで処理します。Embdedは単純に画像をタイル分割するpath-basedな方法と、入力画像にResNet50を適用して得たpixel feature mapをタイル分割してトークン化する方法があります。

Press enter or click to view image in full size

![]()

出典：<https://arxiv.org/pdf/2103.13413>

DPTのDecoderでは、Transformerの各解像度の出力をimage like representationに変換し、Convolutional Networkを使用して、セグメンテーション画像を生成します。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

DPTにはViT-Base、ViT-Large、ViT-Hybridの3つのモデルアーキテクチャが定義されています。ViT-Baseではpatch-basedなembeddingを行い、12のtransformer layersを持ちます。ViT-LargeではViT-Baseと同じembeddingを行いますが、24のtransformer layersとより大きなfeature size Dを持ちます。ViT-HybridではResNet50を使用してembeddingを行い、12のtransformer layersを持ちます。

## DPTの性能

セマンティックセグメンターションタスクにおいて、[150のクラス](https://github.com/CSAILVision/sceneparsing/blob/master/objectInfo150.csv)を持つ大規模なデータセットであるADE20KでSOTAを達成しました。

![]()

出典：<https://arxiv.org/pdf/2103.13413>

また、NYUv2、KITTI、Pscal Contextなどの小規模なデータセットでもfine-tuneすることでSOTAを達成しています。

Press enter or click to view image in full size

![]()

出典：<https://arxiv.org/pdf/2103.13413>

奥行き推定におけるMiDaSとDPTの比較です。DPTは、細部の奥行きをより詳細に予測することができます。また、Convolution Networkでは苦手な、大きな均一領域や、画像内の相対的な位置関係の精度を改善することができます。

Press enter or click to view image in full size

![]()

出典：<https://arxiv.org/pdf/2103.13413>

セグメンテーションモデルでの比較です。DPTは、オブジェクト境界でより詳細な出力を生成する傾向があります。また、いくつかのケースで、出力が乱雑にならない傾向があります。

Press enter or click to view image in full size

![]()

出典：<https://arxiv.org/pdf/2103.13413>

## DPTの使用方法

DPTを使用するには下記のコマンドを使用します。入力画像に対して、セグメンテーションとデプス推定を実行することができます。

```
$ python3 dense_prediction_transformers.py -i input.jpg -s output.png --task=segmentation -e 0  
$ python3 dense_prediction_transformers.py -i input.jpg -s output.png--task=monodepth -e 0
```

[## axinc-ai/ailia-models

### image file (576x384) (Image from…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/image_segmentation/dense_prediction_transformers?source=post_page-----88db4842b4a7---------------------------------------)

実行例です。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。