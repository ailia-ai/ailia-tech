---
title: "YOLOv1 :近年の物体検出の基礎となる高速な物体検出モデル"
author: "Takashi Hatakeyama"
date: 2022-05-26
original_url: https://tech.ailia.ai/yolov1-you-look-only-once高速な物体検出モデル-92141aab4b69
---

# YOLOv1 :近年の物体検出の基礎となる高速な物体検出モデル

# ***YOLOv1 :*** 近年の物体検出の基礎となる***高速な物体検出モデル***

[![Takashi Hatakeyama](../images/yolov1-you-look-only-once__________-92141aab4b69/image_000.jpeg)](https://medium.com/@stayhungry.stayfoolish.1990?source=post_page---byline--92141aab4b69---------------------------------------)

[Takashi Hatakeyama](https://medium.com/@stayhungry.stayfoolish.1990?source=post_page---byline--92141aab4b69---------------------------------------)

May 26, 2022

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「YOLOv1」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

### **YOLOv1の概要**

YOLO（You Look Only Once）は[ワシントン大学](https://www.cs.washington.edu/)の[Joseph Redmon](https://kikaben.com/joseph-redmon-quits-yolo/)らによって開発された物体検出の深層学習モデルです。

[## You Only Look Once: Unified, Real-Time Object Detection

### We present YOLO, a new approach to object detection. Prior work on object detection repurposes classifiers to perform…

arxiv.org](https://arxiv.org/abs/1506.02640?source=post_page-----92141aab4b69---------------------------------------)

YOLOが登場する以前の深層学習の物体検出では、特徴抽出/画像の分類/バウンディングボックスの回帰などプロセスごとにそれぞれ学習が必要でした。 R-CNNの場合、Selective Searchで大量に検出した物体領域候補からCNNにより特徴抽出し、1つ1つをSVMで分類しています。

YOLOの物体検出は、空間的に分離されたバウンディングボックスと関連するクラス確率への回帰問題とする、単一のネットワーク構造となっています。検出パイプライン全体が単一のネットワークであるため、end-to-endで直接最適化できます。

一回の推論で直接バウンディングボックスとクラス確率を予測することが出来るため、YOLOのアーキテクチャは非常に高速です。基本のYOLOモデルは、毎秒45フレームでリアルタイムに画像を処理します。

### YOLOv1のアーキテクチャ

YOLOv1は、画像をSxSグリッドセルに分割します。グリッドセルごとに境界ボックス（≒B）、それらのボックスの信頼度、および各クラス（≒C）の確率を予測します。 これらの予測は、S×S×（B ∗ 5 + C）テンソルとしてエンコードされます。

Press enter or click to view image in full size

![]()

（出典：<https://arxiv.org/abs/1506.02640>）

YOLOv1の構造は非常にシンプルです。入力画像（448×448ピクセル）に畳み込み処理と最大値プーリングを繰り返し施して7×7の大きさまで圧縮します。その際に抽出された特徴量は1024チャンネルの特徴マップになります。

その後に特徴マップがフラット化され、全結合層による処理により7×7×30の出力になります。

## Get Takashi Hatakeyama’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

最終出力の30次元のうち、8次元は回帰ボックスの座標、2次元はボックスの信頼度、20次元はカテゴリ（PASCAL VOCの20クラス）です。

Press enter or click to view image in full size

![]()

（出典：<https://arxiv.org/abs/1506.02640>）

### その他のモデル

### **DPM（Deformable parts models）**

DPMは、オブジェクト検出に”sliding window”アプローチを使用します。 互いに素なパイプラインを使用して、静的な特徴の抽出、領域の分類、高スコア領域の境界ボックスの予測などを行います。

### **R-CNN**

R-CNNは、Edge Boxesなどのアルゴリズムを使用して領域提案を生成します。提案領域はイメージからトリミングされ、サイズ変更されます。その後、トリミングされてサイズ変更された領域は、CNN によって分類されます。最後に、CNN 特徴量を使用して学習したサポート ベクター マシン (SVM) によって、領域提案境界ボックスが調整されます。

### YOLOv1の性能比較

Fast YOLOは、PASCAL VOC検出の記録で最速の検出器であり、他のリアルタイム検出器の2倍の精度を備えています。 YOLOよりも10 mAP精度が下がりますが、リアルタイムの速度をはるかに上回っています。

最近のFasterR-CNNは、最も正確なモデルは7 fpsを達成し、精度の低いモデルは18fpsで実行されます。 FasterR-CNNのVGG-16バージョンは10mAP高くなっていますが、YOLOよりも6倍遅くなっています。

Press enter or click to view image in full size

![]()

### ailia SDKからの使用

ailia SDKを使用することで、Windows、Mac、iOS、Android、LinuxでPythonやUnityからYOLOv1を使用することができます。

ailia SDKとPythonを使用してYOLOv1を実行するサンプルです。

[## axinc-ai/ailia-models

### (Image from…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_detection/yolov1-tiny?source=post_page-----92141aab4b69---------------------------------------)

下記のコマンドで任意の動画に対してYOLOv1を適用可能です。

> *python3* yolov1-tiny.py

![]()

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。

### 参考記事

[YOLOv3 : 物体の位置と種類を検出する機械学習モデル](https://medium.com/axinc/yolov3-66c9b998c096)

[YOLO v4 : 物体を検出する機械学習モデル](https://medium.com/axinc/yolov4-%E7%89%A9%E4%BD%93%E3%82%92%E6%A4%9C%E5%87%BA%E3%81%99%E3%82%8B%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92%E3%83%A2%E3%83%87%E3%83%AB-480f0a635317)