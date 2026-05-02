---
title: "ailia Tokenizer 1.3をリリース"
author: "Kazuki Kyakuno"
date: 2024-08-05
lastmod: 2024-08-05
original_url: https://tech.ailia.ai/ailia-tokenizer-1-3をリリース-75f4d98efe0b
tags: [ailia-sdk]
---

# ailia Tokenizer 1.3をリリース

# ailia Tokenizer 1.3をリリース

[![Kazuki Kyakuno](../images/ailia-tokenizer-1-3_____-75f4d98efe0b/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--75f4d98efe0b---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--75f4d98efe0b---------------------------------------)

7 min read

·

Aug 5, 2024

--

Share

テキストとトークンを相互変換するailia Tokenizer 1.3をリリースしました。新たにPython APIを提供し、ailia MODELSへの適用を行います。

## ailia Tokenizerの概要

ailia Tokenizerは、テキストとトークンを相互変換するライブラリです。AIで自然言語処理する場合、トークナイザを使用して、テキストをAIで扱えるトークンに変換する必要があります。従来、この処理はTransformersで行われていましたが、TransformersはPython APIしか提供されていないため、C++やUnity、Flutterから扱いにくいという課題がありました。ailia Tokenizerは、クロスプラットフォームで利用可能なトークナイザを提供します。

![](../images/ailia-tokenizer-1-3_____-75f4d98efe0b/image_001.png)

ailia Tokenizer 1.3

## ailia Tokenizer 1.3の新機能

### 新しいトークナイザの追加

新しいトークナイザとして、GPT2、LLAMAに対応します。GPT2はGPT2、MSCLAP、BLIP2で、LLAMAはllavaで使用されています。

### 高速化

WhisperやClipのBPEのロジックを見直し、高速化を行なっています。

### Python APIの提供

Transformers互換のAPIを追加し、Pythonから呼び出すことができるようになりました。Transformersは、バックエンドにTensorFlowとTorchを使用しているため、下記の課題があります。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

・ライブラリの読み込みに時間がかかる  
・Dockerで使用した場合にイメージサイズが大きくなる  
・Torchで使用しているcuDNNとailia SDKやONNX RuntimeのcuDNNのバージョンが競合することがある  
・TransformersのAPI仕様の変更により同じ引数でも挙動が変化してモデルが動かなくなる

ailia Tokenizerはこれらの問題を解決し、依存関係の少ない、安定したトークナイザを提供します。

## ailia MODELSにおけるailia Tokenizerの利用

ailia TokenizerのPython APIの提供に伴い、ailia MODELSの全てのモデルでTransformersではなく、ailia Tokenizerを使用するようになりました。

[## GitHub - axinc-ai/ailia-models: The collection of pre-trained, state-of-the-art AI models for ailia…

### The collection of pre-trained, state-of-the-art AI models for ailia SDK - axinc-ai/ailia-models

github.com](https://github.com/axinc-ai/ailia-models?source=post_page-----75f4d98efe0b---------------------------------------)

ailia MODELSの336モデルのうち、Tokenizerを使用するのは下記の39モデルです。

```
audio_processing/clap  
audio_processing/distil-whisper  
audio_processing/msclap  
audio_processing/kotoba-whisper  
diffusion/latent-diffusion-txt2img  
diffusion/stable-diffusion-txt2img  
diffusion/control_net  
diffusion/riffusion  
diffusion/marigold  
image_captioning/blip2  
image_classification/japanese-stable-clip-vit-l-16  
image_classification/japanese-clip  
large_language_model/llava  
natural_language_processing/bert  
natural_language_processing/bert_insert_punctuation  
natural_language_processing/bert_maskedlm  
natural_language_processing/bert_ner  
natural_language_processing/bert_sentiment_analysis  
natural_language_processing/bert_tweet_sentiment  
natural_language_processing/bertjsc  
natural_language_processing/cross_encoder_mmarco  
natural_language_processing/fugumt-en-ja  
natural_language_processing/fugumt-ja-en  
natural_language_processing/multilingual-e5  
natural_language_processing/sentence_transformers_japanese  
natural_language_processing/t5_base_japanese_title_generation  
natural_language_processing/bert_sum_ext  
natural_language_processing/bert_zero_shot_classification  
natural_language_processing/t5_base_japanese_summarization  
natural_language_processing/t5_whisper_medical  
natural_language_processing/gpt2  
natural_language_processing/rinna  
natural_language_processing/bert_question_answering  
natural_language_processing/glucose  
natural_language_processing/bert_maskedlm_proofreeding  
natural_language_processing/soundchoice-g2p  
network_intrucation_detection/bert-network-packet-flow-header-payload  
network_intrucation_detection/falcon-adapter-network-packet  
object_detection/glip
```

下記のオプションを使用することで、従来通り、Transformersを使用することもできます。

```
--disable_ailia_tokenizer
```

## ailia Tokenizerのより詳しい情報

ailia Tokenizerのより詳しい情報は下記の記事を参照してください。

[## ailia Tokenizer : UnityやC++から使用できるNLP向けトークナイザ

### UnityやC++から使用できるNLP向けトークナイザのailia Tokenizerのご紹介です。ailia Tokenizerを使用することで、Python不要で、NLPのトークナイズを行うことが可能です。

medium.com](https://medium.com/axinc/ailia-tokenizer-unity%E3%82%84c-%E3%81%8B%E3%82%89%E4%BD%BF%E7%94%A8%E3%81%A7%E3%81%8D%E3%82%8Bnlp%E5%90%91%E3%81%91%E3%83%88%E3%83%BC%E3%82%AF%E3%83%8A%E3%82%A4%E3%82%B6-b60b68c46b06?source=post_page-----75f4d98efe0b---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。