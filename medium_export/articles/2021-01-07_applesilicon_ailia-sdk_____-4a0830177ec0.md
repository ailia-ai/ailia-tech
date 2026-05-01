---
title: "AppleSiliconでailia SDKを使用する"
author: "Kazuki Kyakuno"
date: 2021-01-07
original_url: https://tech.ailia.ai/applesiliconでailia-sdkを使用する-4a0830177ec0
---

# AppleSiliconでailia SDKを使用する

# AppleSiliconでailia SDKを使用する

[![Kazuki Kyakuno](../images/applesilicon_ailia-sdk_____-4a0830177ec0/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--4a0830177ec0---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--4a0830177ec0---------------------------------------)

Jan 7, 2021

--

Share

クロスプラットフォームで利用できる高速AI推論フレームワークであるailia SDKをAppleSiliconで使用する方法のご紹介です。

## AppleSiliconについて

AppleSiliconはAppleの開発したSoCの名称です。armアーキテクチャで、強力なCPUとGPUを搭載しています。AppleSiliconの第一世代のM1チップはGeForce GTX1060クラスのGPUを搭載しており、ailia SDKを使用することでGPUを使用した高速なAI推論が可能です。IntelアーキテクチャのMacBookProに比べて、YOLOv3 fullが5倍近い速度で動作します。

Press enter or click to view image in full size

![]()

出典：<https://www.apple.com/jp/mac/m1/>

## AppleSiliconでPythonを動かす

macOS Big SurにはPython3.8がプリインストールされており、ユニバーサルバイナリになります。ライブラリを格納するSite-Packagesは共通で、ユニバーサルバイナリであればx86\_64とarm64のどちらからでも使用できます。しかし、依存するライブラリが一つでもx86\_64の場合は、x86\_64で動作させる必要があります。

ailia SDKはx86\_64とarm64のユニバーサルバイナリになっています。しかし、現在はOpenCVのarm64バイナリが提供されていないため、現状ではRosetta2のx86\_64エミュレーションで動作させる必要があります。エミュレーションとはいえ、ailia SDKはMetalのシェーダで動作するため、大幅な高速化が実現します。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Python3.8をx86\_64モードで動作させるには、アプリケーション/ユーティリティフォルダにあるTerminalをコピーし、右クリックして、情報を見るから、Rosettaを使用して開くにチェックを入れます。

![]()

そうすると、x86\_64モードでPythonを実行することができ、pip3でopencv-pythonをインストールすることができます。

> pip3 install opencv-python

## AppleSiliconにailia SDKをインストールする

x86\_64モードでもarmモードでもどちらのターミナルでも下記のコマンドでailia SDKをインストール可能です。

> cd ailia\_sdk/python  
> python3 bootstrap.py  
> pip3 install ./

[## ailia SDK チュートリアル(Python)

### ailia SDKをPythonで使用するチュートリアルです。Pythonを使用することで様々なモデルの動作を簡単に試すことができます。

medium.com](https://medium.com/axinc/ailia-sdk-%E3%83%81%E3%83%A5%E3%83%BC%E3%83%88%E3%83%AA%E3%82%A2%E3%83%AB-python-28379dbc9649?source=post_page-----4a0830177ec0---------------------------------------)

## AppleSiliconでailia MODELSを動かす

githubのailia MODELSをcloneします。

[## axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art models. ailia SDK is a cross-platform high speed inference SDK. The…

github.com](https://github.com/axinc-ai/ailia-models?source=post_page-----4a0830177ec0---------------------------------------)

x86\_64モードのターミナルから下記を実行します。

> python3 launch.py

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。