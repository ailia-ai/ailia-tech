---
title: "StableDiffusionWebUIとControlNetを使って任意ポーズの画像を生成する"
author: "Kazuki Kyakuno"
date: 2023-04-18
original_url: https://tech.ailia.ai/stablediffusionwebuiでcontrolnetを使って任意ポーズの画像を生成する-bc91563cf7f3
---

# StableDiffusionWebUIとControlNetを使って任意ポーズの画像を生成する

# StableDiffusionWebUIとControlNetを使って任意ポーズの画像を生成する

[![Kazuki Kyakuno](../images/stablediffusionwebui_controlnet_________________-bc91563cf7f3/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--bc91563cf7f3---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--bc91563cf7f3---------------------------------------)

12 min read

·

Apr 6, 2023

--

Share

PC上で簡単にイラストを生成するStableDiffusionWebUIと、イラストに制約をかけるControlNetを使用することで、任意ポーズの画像を生成する方法を解説します。

## StableDiffusion、ControlNetについて

StableDiffusionは任意のテキストからイラストを生成することができるAIモデルです。StableDiffusionには各種の拡張を行うことができ、ControlNetを使用することでポーズなどの指定が可能です。

今回、検証に使用したバージョンは下記です。

```
Windows 10  
Python 3.10.9  
StableDiffusionWebUI = 22bcc7be428c94e9408f589966c2040187245d81  
sd-webui-controlnet = 241c05f8 (Thu Mar 23 15:18:35 2023)
```

## StableDiffusionWebUIについて

[StableDiffusionWebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)はPC上で簡単にStableDiffusionを使用することができるWEBフロントエンドです。NVIDIAのRTXシリーズのGPUを搭載したWindows PCに、[Git](https://gitforwindows.org/)と[Python](https://www.python.org/downloads/release/python-3106/)をインストールした上で、下記のコマンドを実行することでインストールと実行が可能です。

```
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git  
cd .\stable-diffusion-webui\  
.\webui-user.bat
```

実行後、表示されたURLにブラウザからアクセスすると操作可能になります。下記の例ではhttp://127.0.0.1:7860に接続します。

```
Model loaded in 9.5s (calculate hash: 3.5s, load weights from disk: 0.1s, create model: 2.9s, apply weights to model: 0.7s, apply half(): 0.6s, move model to device: 1.0s, load textual inversion embeddings: 0.7s).  
Running on local URL:  http://127.0.0.1:7860
```

接続するとWEB UIが表示されます。txt2imgのタブでテキストを入れてGenerateを押すと画像が生成されます。

Press enter or click to view image in full size

![]()

anime girl faceで生成

## モデルファイルの変更

StableDiffusionには各種の派生のモデルファイルが存在します。モデルファイルはsafetensors形式になっており、ダウンロードしてmodelsフォルダに配置することで使用することが可能です。

まず、Basil\_mix\_fixed.safetensorsをダウンロードして\stable-diffusion-webui\models\Stable-diffusionに配置します。このモデルファイルはRealistic texture and Asian faceでFine Tuningされたモデルです。

[## Basil\_mix\_fixed.safetensors · nuigurumi/basil\_mix at main

### Upload Basil\_mix\_fixed.safetensors 447b3e6 This file is stored with Git LFS . It is too big to display, but you can…

huggingface.co](https://huggingface.co/nuigurumi/basil_mix/blob/main/Basil_mix_fixed.safetensors?source=post_page-----bc91563cf7f3---------------------------------------)

次に、vae-ft-mse-840000-ema-pruned.safetensorsを\stable-diffusion-webui\models\VAEに配置します。VAEは後処理用のモデルです。sd-vae-ft-mse-originalは生成された顔を補正する効果があります。StableDiffusionの画像の破綻をリカバリーします。

[## vae-ft-mse-840000-ema-pruned.safetensors · stabilityai/sd-vae-ft-mse-original at main

### Adding `safetensors` variant of this model (#1) 629b3ad This file is stored with Git LFS . It is too big to display…

huggingface.co](https://huggingface.co/stabilityai/sd-vae-ft-mse-original/blob/main/vae-ft-mse-840000-ema-pruned.safetensors?source=post_page-----bc91563cf7f3---------------------------------------)

![]()

モデルファイルの配置

モデルファイルの配置が終わったら、WEB UIの左上のモデル選択のリフレッシュマークを押し、リストボックスから選択することで、ダウンロードしたモデルが使用可能です。

Press enter or click to view image in full size

![]()

モデルの読み込み

VAEモデルはSettingsのStable Diffusion -> SD VAEで選択します。

Press enter or click to view image in full size

![]()

VAEの選択

モデルを変更して、同じPromptで画像を生成すると、下記のようになります。より写実的な画像が出力されます。

Press enter or click to view image in full size

![]()

anime girl faceで生成

## ControlNetのインストール

標準のStableDiffusionでは、テキストでしかイラストの出力を制御できません。ControlNetを使用すると、骨格や線画、セグメンテーションを使用してイラストの出力を制御することが可能です。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

ControlNetは、StableDiffusionWebUIのプラグインとしてインストール可能です。StableDiffusionWebUIのExtensionsのInstall from URLに <https://github.com/Mikubill/sd-webui-controlnet> を指定してインストールします。

Press enter or click to view image in full size

![]()

ControlNetのインストール

インストール後、Apply and restart UIを押します。

Press enter or click to view image in full size

![]()

再起動

リロードすると、txt2imgにcontrolnetが増えています。

Press enter or click to view image in full size

![]()

ControlNetの項目

次に、モデルファイルをダウンロードします。骨格で制御するため、control\_openpose-fp16.safetensorsを\stable-diffusion-webui\models\ControlNet/に配置します。

[## control\_openpose-fp16.safetensors · webui/ControlNet-modules-safetensors at main

### This file is stored with Git LFS . It is too big to display, but you can still download it. SHA256…

huggingface.co](https://huggingface.co/webui/ControlNet-modules-safetensors/blob/main/control_openpose-fp16.safetensors?source=post_page-----bc91563cf7f3---------------------------------------)

![]()

ControlNetのモデルの配置

WebUIに戻って、ControlNetのタブを開くと下記になります。Enableを押して、PreprocessorにOpenPoseを指定します。任意の画像をアップロードして、Preview Annotate Resultを押します。

Press enter or click to view image in full size

![]()

骨格推定結果

うまく骨格が推定できたら、Modelにcontrol\_sd15\_openposeを指定します。モデルが表示されない場合は青い再読み込みボタンを押してください。

Press enter or click to view image in full size

![]()

モデル選択

この状態で、Generateをします。

Press enter or click to view image in full size

![]()

指定したポーズで画像が生成される

Press enter or click to view image in full size

![]()

anime girlで生成された画像

指定したポーズで画像が生成されました。

## PoseではなくSegmentationで制約をかける

次に、骨格ではなく、セグメンテーションから画像を生成します。骨格よりもセグメンテーションの方が情報量が多いため、セグメンテーションでポーズ指定した方がより正確なポーズの画像が生成されます。

モデルファイルをダウンロードします。セグメンテーションで制御するため、control\_seg-fp16.safetensorsを\stable-diffusion-webui\models\ControlNet/に配置します。

[## control\_seg-fp16.safetensors · webui/ControlNet-modules-safetensors at main

### This file is stored with Git LFS . It is too big to display, but you can still download it. SHA256…

huggingface.co](https://huggingface.co/webui/ControlNet-modules-safetensors/blob/main/control_seg-fp16.safetensors?source=post_page-----bc91563cf7f3---------------------------------------)

Preprocessorにsegmentation、Modelにcontrol\_seg-fp16を指定します。

Press enter or click to view image in full size

![]()

セグメンテーションによる制約

生成します。

Press enter or click to view image in full size

![]()

生成

生成された画像です。より正確なポーズが反映されます。背景の特徴も反映されています。

Press enter or click to view image in full size

![]()

anime girlで生成された画像

## ControlNetの動作原理

ControlNetのソースコードと論文は下記にあります。

[## GitHub - lllyasviel/ControlNet: Let us control diffusion models!

### Official implementation of Adding Conditional Control to Text-to-Image Diffusion Models. ControlNet is a neural network…

github.com](https://github.com/lllyasviel/ControlNet?source=post_page-----bc91563cf7f3---------------------------------------)

ControlNetは、StableDiffusionの中間レイヤーへの加算値を学習します。

![]()

ControlNetの基本構造（出典：<https://arxiv.org/pdf/2302.05543.pdf>）

過学習を防ぐために、StableDiffusionのレイヤーのウエイトは固定し、ZeroConvolutionという、カーネルサイズ1x1、weight = 0、bias = 0のレイヤーを挟むことで、初期状態ではStableDiffusionと全く同じ状態からスタートします。

![]()

ControlNetの全体構造（出典：<https://arxiv.org/pdf/2302.05543.pdf>）

そこから、ZeroConvolutionがBackPropagationによって重みを学習し、通常の1x1 Convolutionに変化していきます。この、ゆっくり差分を学習していく構造により、少量のデータで学習できるようになっています。

基盤モデル側のWeightを固定し、FeatureVectorの差分を学習する方法はAdapterと呼ばれており、基盤モデルをFine Tuningする手法として有力と言われています。

[## GitHub - gaopengcuhk/CLIP-Adapter

### Official implementation of 'CLIP-Adapter: Better Vision-Language Models with Feature Adapters'. CLIP-Adapter is a…

github.com](https://github.com/gaopengcuhk/CLIP-Adapter?source=post_page-----bc91563cf7f3---------------------------------------)

ControlNetは標準のStableDiffusionの重み以外のBasilMixなどのモデルに対して適用しても、正常な出力が得られます。

アーキテクチャ的にはStableDiffusionの重みは学習時のものをそのまま使わないと誤差が出そうですが、他のStableDiffusionの重みもClipEmbeddingが共通なので、そこである程度縛られ、意外と再学習しなくても動いているという印象を持っています。

## まとめ

StableDiffusionとControlNetによって、Prompt以外でも出力を制御できるようになり、狙ったイラストを生成しやすくなりました。次回は、LoRAによるキャラクターの固定化についてご紹介する予定です。

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。