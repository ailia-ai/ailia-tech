---
title: "PytorchDcTts : テキストから音声合成を行う機械学習モデル"
author: "Kazuki Kyakuno"
date: 2021-05-11
lastmod: 2021-05-11
original_url: https://medium.com/axinc/pytorchdctts-テキストから音声合成を行う機械学習モデル-dcb5eb07c883
tags: [ailia-models]
---

# PytorchDcTts : テキストから音声合成を行う機械学習モデル

# PytorchDcTts : テキストから音声合成を行う機械学習モデル

[![Kazuki Kyakuno](../images/pytorchdctts-____________________-dcb5eb07c883/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--dcb5eb07c883---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--dcb5eb07c883---------------------------------------)

May 11, 2021

--

Share

[ailia SDK](https://ailia.jp/)で使用できる機械学習モデルである「PytorchDcTts」のご紹介です。エッジ向け推論フレームワークである[ailia SDK](https://ailia.jp/)と[ailia MODELS](https://github.com/axinc-ai/ailia-models)に公開されている機械学習モデルを使用することで、簡単にAIの機能をアプリケーションに実装することができます。

## PytorchDcTtsの概要

PytorchDcTts（Pytorch Deep Convolutional Text-to-Speech）は2017年10月に公開された機械学習モデルです。テキストを入力して音声ファイルを出力することができます。

[## Efficiently Trainable Text-to-Speech System Based on Deep Convolutional Networks with Guided…

### This paper describes a novel text-to-speech (TTS) technique based on deep convolutional neural networks (CNN), without…

arxiv.org](https://arxiv.org/abs/1710.08969?source=post_page-----dcb5eb07c883---------------------------------------)

## PytorchDcTtsのアーキテクチャ

音声合成のタスクでは、一般的にRNN（再帰的ニューラルネットワーク）が使用されますが、学習に時間がかかるという問題があります。この問題に対して、PytorchDcTtsはCNNで音声合成を構成することで、一般的なゲーミングPCで15時間程度で学習できるようにしています。

ディープラーニングを使用しない音声合成は、複数のコンポーネントを使用した複雑なシステムでした。例えば、text analyzer、F0 generator、spectrum generator、pause estimator、vocodarの組み合わせになります。

ディープラーニングによって、これらの複数のコンポーネントはend-to-endの1つのモデルに集約され、inputからoutputをダイレクトに計算可能にします。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

PytorchDcTtsのモデルアーキテクチャは下記となります。TextEncでInput Textをベクトル化、AttentionでTextとMelspectrogramのペアを算出して重み付け、AudioDecでMelspectrumを計算、SSRN（Spectrogram Super-resolution Netrowk）で音声の品質改善を行います。

![](../images/pytorchdctts-____________________-dcb5eb07c883/image_001.png)

出典：<https://arxiv.org/pdf/1710.08969>

音声合成の例です。上から、Attention、mel spectrogram、linear STFT spectrogramです。

Press enter or click to view image in full size

![](../images/pytorchdctts-____________________-dcb5eb07c883/image_002.png)

出典：<https://arxiv.org/pdf/1710.08969>

学習用のデータセットとしてLJ Speech Datasetを使用します。これは、13Kのテキストとスピーチのペアのデータセットです。合計で24時間のデータ量があります。

[## The LJ Speech Dataset

### This is a public domain speech dataset consisting of 13,100 short audio clips of a single speaker reading passages from…

keithito.com](https://keithito.com/LJ-Speech-Dataset/?source=post_page-----dcb5eb07c883---------------------------------------)

## PytorchDcTtsの使用方法

下記のコマンドで任意のテキスト（英語）からwavファイルを出力することができます。

```
python3 pytorch-dc-tts.py -i "Hello world" -s output.wav
```

実行例は下記です。

[## axinc-ai/ailia-models

### A sentence which is defined as SENTENCE in pytorch-dc-tts.py. The Voice file is output as .wav which path is defined as…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/pytorch-dc-tts?source=post_page-----dcb5eb07c883---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。