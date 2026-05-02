---
title: "MobileObjectLocalizer : 任意の物体を検出できる物体検出モデル"
author: "Kazuki Kyakuno"
date: 2021-12-21
lastmod: 2021-12-24
original_url: https://medium.com/axinc/mobileobjectlocalizer-任意の物体を検出できる物体検出モデル-595b54cfab26
tags: [ailia-models]
---

# MobileObjectLocalizer : 任意の物体を検出できる物体検出モデル

# MobileObjectLocalizer : 任意の物体を検出できる物体検出モデル

[![Kazuki Kyakuno](../images/mobileobjectlocalizer-__________________-595b54cfab26/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--595b54cfab26---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--595b54cfab26---------------------------------------)

Dec 21, 2021

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「MobileObjectLocalizer」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## MobileObjectLocalizerについて

MobileObjectLocalizerはGoogleが開発した、物体の種別を問わない汎用の物体検出モデルです。通常のYOLOでは、COCOの80クラスの認識を行いますが、MobileObjectLocalizerはクラスが定義されておらず、任意の物体を検出することが可能です。

![](../images/mobileobjectlocalizer-__________________-595b54cfab26/image_001.png)

出典：<https://pixabay.com/photos/hot-air-balloons-sky-sunrise-dawn-4561263/>

[## TensorFlow Hub

### Edit description

tfhub.dev](https://tfhub.dev/google/object_detection/mobile_object_localizer_v1/1?source=post_page-----595b54cfab26---------------------------------------)

## MobileObjectLocalizerのアーキテクチャ

MobileObjectLocalizerはMobileNetV2とSSD-Liteを使用しています。入力解像度は192x192で、最大で100個のBoundingBoxが出力されます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

精度はそこまで高くないものの、学習不要で任意の物体のBoundingBoxを検出可能です。そのため、後段にResNet50を入れて1000クラスの識別器を作ったり、画面に映っている最もConfidence値の高いBoundingBoxを検出することでオートフォーカスに使用したりなど、いろいろな応用に使用することが可能です。

## MobileObjectLocalizerの使用方法

ailia SDKでMobileObjectLocalizerを使用するには下記のコマンドを使用します。

```
$ python3 mobile_object_localizer.py -v 0
```

[## ailia-models/object\_detection/mobile\_object\_localizer at master · axinc-ai/ailia-models

### (Image from https://commons.wikimedia.org/wiki/File:Il\_cuore\_di\_Como.jpg) Shape : (1, 3, 192, 192) detection\_boxes…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_detection/mobile_object_localizer?source=post_page-----595b54cfab26---------------------------------------)

実行例です。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。