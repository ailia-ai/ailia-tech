---
title: "MMDetectionのモデルをONNX形式にエクスポートする"
author: "Satoshi Ooe"
date: 2020-10-02
lastmod: 2020-10-02
original_url: https://medium.com/axinc/mmdetectionのモデルをonnxにエクスポートする-d2f249ca01be
tags: [ailia-technology]
---

# MMDetectionのモデルをONNX形式にエクスポートする

# MMDetectionのモデルをONNX形式にエクスポートする

[![Satoshi Ooe](../images/mmdetection_____onnx_________-d2f249ca01be/image_000.jpeg)](https://medium.com/@satoshiooe?source=post_page---byline--d2f249ca01be---------------------------------------)

[Satoshi Ooe](https://medium.com/@satoshiooe?source=post_page---byline--d2f249ca01be---------------------------------------)

5 min read

·

Oct 2, 2020

--

Share

[MMDetection](https://github.com/open-mmlab/mmdetection)は、PyTorchに基づくオープンソースのオブジェクト検出ツールボックスです。MMDetectionのモデルをailia SDKで使用するONNX形式にエクスポートする手順について解説します。ailia SDKについては[こちら](https://ailia.jp/)をご覧ください。

Press enter or click to view image in full size

![](../images/mmdetection_____onnx_________-d2f249ca01be/image_001.png)

出典：<https://github.com/open-mmlab/mmdetection>

## MMDetectionモデルの構造

MMDetectionのモデルは、ニューラルネットワークの設計を現す ”configファイル” と学習済みのパラメータを現す”checkpointファイル” の二つのファイルから構成されます。

configファイルはPythonのコード形式で記述されたテキストファイルで、変数名やデータ構造をMMDetectionの定義ルールに従って記述します。例えば、以下のような内容になります。

configファイルの構造は、MMDetectionのドキュメントサイトに解説があります。（ドキュメントサイトのリンクは[こちら](https://mmdetection.readthedocs.io/en/latest/index.html)）

[## Config System - MMDetection 2.4.0 documentation

### To help the users have a basic idea of a complete config and the modules in a modern detection system, we make brief…

mmdetection.readthedocs.io](https://mmdetection.readthedocs.io/en/latest/config.html?source=post_page-----d2f249ca01be---------------------------------------)

## 公式の変換スクリプト

公式の変換スクリプトが用意されていて、これを使ってMMDetectionのモデルをONNX形式にエクスポートすることができます。（スクリプトのリンクは[こちら](https://github.com/open-mmlab/mmdetection/blob/master/tools/pytorch2onnx.py)）

```
python3 tools/pytorch2onnx.py <config file> <checkpoint file> --out <out.onnx> --shape 1120 768
```

引数に ”configファイル” と ”checkpointファイル” のパスを指定し、 `--out` パラメータで作成するONNXファイルの名前を指定し、 `--shape` パラメータで入力テンソルのshapeを指定します。

## OTEDetection

MMDetectionは、ONNXのエクスポートに対してまだ充分に対応していないため、 `pytorch2onnx.py`を使ったエクスポートはうまくいかないかもしれません。

## Get Satoshi Ooe’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

そこでMMDetectionをベースに開発され、多くのモデルのONNXエクスポートに対応できるようにした [OTEDetection](https://github.com/openvinotoolkit/mmdetection) を使用します。OTEDetectionは、SSD, FCOS, ATSS, FoveaBox, Faster & Mask R-CNN, Cascade & Cascade Mask R-CNN など多くのモデルのONNXエクスポートに対応しています。

[## OTEDetection - openvinotoolkit/mmdetection

### This is an Object Detection and Instance Segmentation toolbox, that is a part of OpenVINO Training Extensions. Project…

github.com](https://github.com/openvinotoolkit/mmdetection?source=post_page-----d2f249ca01be---------------------------------------)

[## End-to-end Faster/Mask R-CNN models export to ONNX by druzhkov-paul · Pull Request #1386 ·…

### Since primitives like ROIAlign and NonMaxSuppression required for most of the detection/instance segmentation models…

github.com](https://github.com/open-mmlab/mmdetection/pull/1386?source=post_page-----d2f249ca01be---------------------------------------#issuecomment-639382141)

OTEDetectionの変換スクリプトは以下のように実行します。（スクリプトのリンクは[こちら](https://github.com/openvinotoolkit/mmdetection/blob/ote/tools/export.py)）

```
python3 tools/export.py <config file> <checkpoint file> <output dir> onnx
```

## Version2形式へのアップデート

OTEDetectionは、MMDetectionのバージョン2をベースにしており、バージョン1形式のモデルファイルとは互換性がありません。バージョン1形式で作成されたモデルファイルをONNX形式にエクスポートするためには、まずバージョン2形式へ変換を行う必要があります。

モデルのconfigファイルは、MMDetectionのドキュメントサイトの説明を参考に、テキストベースでの編集を行います。configファイルの詳細な説明は[こちら](https://github.com/openvinotoolkit/mmdetection/blob/ote/tools/upgrade_model_version.py)をご覧ください。

checkpointファイルは、変換ツールが用意されているので、それを使って以下のように実行します。（変換ツールのリンクは[こちら](https://github.com/openvinotoolkit/mmdetection/blob/ote/tools/upgrade_model_version.py)）

```
python tools/upgrade_model_version.py <checkpoint file v1> <output file>
```

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。