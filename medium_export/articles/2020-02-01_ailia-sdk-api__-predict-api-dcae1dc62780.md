---
title: "ailia SDK API解説(Predict API)"
author: "Kazuki Kyakuno"
date: 2020-02-01
lastmod: 2020-12-13
tags: [ailia-tutorial]
original_url: https://tech.ailia.ai/ailia-sdk-api解説-predict-api-dcae1dc62780
---

# ailia SDK API解説(Predict API)

# ailia SDK API解説(Predict API)

[![Kazuki Kyakuno](../images/ailia-sdk-api__-predict-api-dcae1dc62780/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--dcae1dc62780---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--dcae1dc62780---------------------------------------)

Feb 1, 2020

--

Share

ailia SDKのコアAPIであるPredict APIの解説です。ailia SDKを利用することでディープラーニングの推論をGPUを使用して高速に行うことができます。ailia SDKについて詳しくは[こちら](https://ailia.jp/)をご覧ください。

## Predict APIの概要

Predict APIはテンソルを入力してテンソルを出力する最も基本的なAPIです。1入力1出力のモデルだけでなく、複数入力・複数出力のモデルも扱うことができます。

## 1入力1出力を持つモデルの推論

CのAPIはlibrary/include/ailia.hに、PythonのAPIはpython/ailia/\_\_init\_\_.pyに、C#のAPIはunity/Assets/AILIA/Scripts/Models/AiliaModel.csに定義されています。

Press enter or click to view image in full size

![](../images/ailia-sdk-api__-predict-api-dcae1dc62780/image_001.png)

Predict APIを使用して1入力1出力のモデルを推論する流れです。

(1) ailiaCreateでインスタンス作成  
(2) ailiaOpenStreamFileおよびailiaOpenWeightFileでモデルを読み込み  
(3) ailiaGetInputShapeで入力形状を取得  
(4) ailiaGetOutputShapeで出力形状を取得  
(5) ailiaPredictに入出力テンソルのfloat配列を与えて推論  
(6) ailiaDestroyでインスタンス解放

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Cでのコード例です。CのAPIはC99で定義されています。C++はABIが標準化されておらず、異なるコンパイラを使用した場合に互換性の問題が発生するため、C99で定義しています。将来的に、C++用のラッパーのヘッダファイルでの提供を計画しています。

C#でのコード例です。C#ではAiliaModelクラスを使用します。ailiaCreate、ailiaOpenStreamFile、ailiaOpenWeightFileがAiliaModel.Openに統合されています。

Pythonでのコード例です。PythonではAilia.Netクラスを使用します。ailiaCreate、ailiaOpenStreamFile、ailiaOpenWeightFileがailia.Netのコンストラクタに統合されています。

## 複数の入出力を持つモデルの推論

複数の入出力のモデルを推論する流れです。

(1) ailiaCreateでインスタンス作成  
(2) ailiaOpenStreamFileおよびailiaOpenWeightFileでモデルを読み込み  
(3) ailiaFindBlobIndexByNameとailiaGetBlobShapeで入力形状を取得  
(4) ailiaFindBlobIndexByNameとailiaGetBlobShapeで出力形状を取得  
(5) ailiaSetInputBlobDataで入力テンソルのfloat配列を与える  
(6) ailiaUpdateで推論  
(7) ailiaGetBlobDataで出力テンソルのfloat配列を与えて推論結果を取得  
(8) ailiaDestroyでインスタンス解放

C言語でのコード例です。

C#でのコード例です。C#による複数入出力はailia SDK 1.2.1からの対応となります。

Pythonでのコード例です。

## バックエンドの選択

ailia SDKの現在のバージョンでは、AILIA\_ENVIRONMENT\_ID\_AUTOを与えるとCPUで実行します。GPUを使用する場合、ailiaGetEnvironmentでGPUのenv\_idを指定したあと、ailiaCreateにGPUのenv\_idを与えてください。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。