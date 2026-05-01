---
title: "SberSwap : AIによる高精度なFaceSwap"
author: "Kazuki Kyakuno"
date: 2024-08-22
original_url: https://tech.ailia.ai/sberswap-aiによる高精度なfaceswap-bddae3b8ff84
---

# SberSwap : AIによる高精度なFaceSwap

# SberSwap : AIによる高精度なFaceSwap

[![Kazuki Kyakuno](../images/sberswap-ai_______faceswap-bddae3b8ff84/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--bddae3b8ff84---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--bddae3b8ff84---------------------------------------)

8 min read

·

Oct 26, 2023

--

Share

AIによる高精度なFaceSwapを行うSberSwapのご紹介です。SberSwapを使用することで、静止画や動画の顔を別人に置き換えることが可能です。

## SberSwapの概要

SberSwapは2022年4月に公開されたFaceSwapモデルです。現在はGhostという名前に改名しており、GhostとSberSwapは同じ技術になります。

[## GitHub - ai-forever/ghost: A new one shot face swap approach for image and video domains

### A new one shot face swap approach for image and video domains - GitHub - ai-forever/ghost: A new one shot face swap…

github.com](https://github.com/ai-forever/ghost?source=post_page-----bddae3b8ff84---------------------------------------)

[## GHOST-A New Face Swap Approach for Image and Video Domains

### Deep fake stands for a face swapping algorithm where the source and target can be an image or a video. Researchers have…

ieeexplore.ieee.org](https://ieeexplore.ieee.org/abstract/document/9851423?source=post_page-----bddae3b8ff84---------------------------------------)

## SberSwapの概要

FaceSwapは、映画産業や、顔のメイクアップ、ヘアスタイリング、顔検出及び認識モデルの学習用データセットの作成に利用されています。

Face Swapでは、従来、GANやAutoEncoderが使用されてきました。しかし、既存の手法では、視覚的なアーティファクトが存在しました。また、多くの技術は静止画向けであったため、動画への適用に弱いという課題がありました。

SberSwapでは、新しいFaceShifterアーキテクチャを採用し、目に注目した損失関数、顔マスクのスムージング、動画のための隣接フレーム間のスムージング、顔画像の超解像など、複数の技術で品質を改善します。

## SberSwapのアーキテクチャ

SberSwapのアーキテクチャは下記となります。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

最初にSource ImageとTarget Imageの顔の領域を検知し、アフィン変換を行なって角度を正規化します。次に、両方の顔画像をAIモデルに入力し、FaceSwap Imageを生成します。生成したFaceSwap Imageを、Facial Keypointから生成したマスクを使ってTarget Imageとブレンドします。最後に、FaceSwap Imageをアフィン逆変換し、元のフレームに合成します。

Press enter or click to view image in full size

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

FaceSwapのAIモデルのモデルアーキテクチャです。FaceSwapのAIモデルでは、Target Imageの256x256の顔画像と、Source Imageの256x256の顔画像を入力とします。Target Imageはそのまま、Source Imageは112x112のArcFaceを適用した512次元のEmbeddingを計算します。Generatorでは、Target Imageと、Source ImageのEmbeddingを入力とし、FaceSwapした顔画像を出力します。

Press enter or click to view image in full size

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

FaceSwap Imageはそのまま使用せず、Facial Landmarksから計算したマスクを使用して、Target Imageと合成します。Facial Landmarksの検出には192x192解像度のMXNetを使用しています。

Press enter or click to view image in full size

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

マスクにはSmoothingを適用します。Binary maskを使用した場合と、Smooth maskを使用した場合の画質の比較です。Smooth maskを使用したほうが、滑らかな出力が得られます。

Press enter or click to view image in full size

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

最後に、ブレンド後の顔画像に対して、Pix2Pixの超解像処理を行います。これにより、顔画像が鮮明化されます。入力と出力の解像度は共に256x256です。

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

モデルアーキテクチャごとの画質の比較です。最終的に、Unetが使用されています。

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

モデル内のブロック数ごとの画質の比較です。最終的に、2blocksが使用されています。

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

損失関数の比較です。Eye lossを使用することで、精度が改善します。

![]()

出典：<https://ieeexplore.ieee.org/abstract/document/9851423>

## SberSwapの使用方法

ailia SDKでSberSwapを使用するには、下記のコマンドを使用します。target.jpgの顔を、source.jpgの顔に置き換え、output.jpgを出力します。

```
$ python3 sber-swap.py --input target.jpg --source source.jpg --savepath output.jpg
```

videoオプションを適用することで、動画に対して適用することも可能です。

```
$ python3 sber-swap.py --video target.mp4 --source source.jpg --savepath output.mp4
```

また、 — usr\_srオプションで、face enhanceを適用することも可能です。

```
$ python3 sber-swap.py --use_sr
```

[## ailia-models/face\_swapping/sber-swap at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK - ailia-models/face\_swapping/sber-swap at…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/face_swapping/sber-swap?source=post_page-----bddae3b8ff84---------------------------------------)

なお、現状、1人のFaceSwapしか行うことはできません。原理的には、ByteTrackなどのトラッキングアルゴリズムと併用すれば、複数人のFaceSwapも可能です。

## ailia SDKを使用するメリット

公式のSberSwapはMXNet (CUDA)、ONNX Runtime (CUDA)、Torch (CUDA)の3つのフレームワークを使用しています。具体的に、FaceDetectionはMXNet、ArcFaceはTorch、LandmarkDetectorはONNX Runtime、GeneratorはTorchを使用しています。

特に、MXNetはnumpy1.23以下が必要、ONNX Runtimeはnumpy1.24.2以降が必要など、バージョンがコンフリクトすることがあります。また、CUDAの環境でしか動作しないため、macOSなどで実行できないという課題もあります。

ailia MODELSバージョンのSberSwapを使用することで、フレームワークとしてはailia SDKだけで実装が可能であり、numpyやCUDAのバージョンも一つに統一できるため、長期メンテナンスに最適です。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。