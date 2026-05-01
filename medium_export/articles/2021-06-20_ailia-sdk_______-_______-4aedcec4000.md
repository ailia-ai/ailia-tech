---
title: "ailia SDKチュートリアル（省メモリモード）"
author: "Kazuki Kyakuno"
date: 2021-06-20
original_url: https://tech.ailia.ai/ailia-sdkチュートリアル-省メモリモード-4aedcec4000
---

# ailia SDKチュートリアル（省メモリモード）

# ailia SDKチュートリアル（省メモリモード）

[![Kazuki Kyakuno](../images/ailia-sdk_______-_______-4aedcec4000/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--4aedcec4000---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--4aedcec4000---------------------------------------)

9 min read

·

Jun 20, 2021

--

Share

ailia SDKはクロスプラットフォームの推論エンジンです。ailia SDKを使用することで、機械学習モデルを省メモリで推論することが可能です。ailia SDKについては[こちら](https://ailia.jp/)をご覧ください。

## 機械学習モデルのメモリ管理

機械学習モデルの推論では、入力されたテンソルを計算グラフに通していくことで出力テンソルを得ます。その際、計算グラフの中間出力となるテンソルをCPUやGPUのメモリ空間に確保します。

![]()

中間テンソルの例

ActivationやBatchNormalizationの中間テンソルについてはレイヤーフュージョンによって自動的に削除されます。

それ以外の中間テンソルは、デフォルトでは速度を優先して別メモリに確保されます。実際の出力とならない中間テンソルは一時メモリであるため、都度、確保と開放を行うことで省メモリ化が可能です。

## 省メモリモードの概要

モバイルデバイスでの推論や、マネージドサーバでの推論など、使用可能なメモリが制限される用途においては、省メモリモードとして、Reduce InterstageとReuse Interstageという2つのメモリモードを選択可能です。

Reduce Interstageでは、テンソルが必要とされるタイミングでメモリを確保し、使用が終わったら都度、メモリを開放します。これにより、最も省メモリとなります。ただし、都度、メモリの確保・開放が走るため、推論速度が遅くなります。1回だけ推論するような処理に最適です。

Reuse Interstageでは、同じサイズのテンソルでメモリを共有します。機械学習モデルでは、同じサイズのConv -> Activationを複数回、繰り返すような処理が多く発生するため、速度をあまり落とさずにメモリ消費量を削減することができます。ただし、モデルによっては、並列演算可能なグラフが直列演算となるため、速度が低下する場合があります。

Reduce InterstageおよびReuse Interstageの注意点として、output指定されていない中間テンソルを削除するため、中間テンソルを取得して使用するPaDiMのようなモデルでは使用できません。削除されたテンソルをget\_input\_blob\_data APIで取得しようとすると、AILIA\_STATUS\_DATA\_REMOVEDエラーが返ります。

## 省メモリモードの使用方法

Python APIではailia.get\_memory\_modeで取得したメモリモードをailia.Netインスタンスに与えます。

> memory\_mode=ailia.get\_memory\_mode(True,True,True,False)  
> net = ailia.Net(MODEL\_PATH, WEIGHT\_PATH, env\_id=args.env\_id, memory\_mode=memory\_mode)

C++ APIではAILIA\_MEMORY\_\*をAILIANetworkインスタンスに与えます。OpenStreamFileを呼び出す前に実行する必要があります。

> ailiaSetMemoryMode(instance, AILIA\_MEMORY\_OPTIMAIZE\_DEFAULT | AILIA\_MEMORY\_REDUCE\_INTERSTAGE)

Unity APIでは下記のように、Ailia.AILIA\_MEMORY\_\*をAiliaModelインスタンスに与えます。Openを呼び出す前に実行する必要があります。

> model.SetMemoryMode(Ailia.AILIA\_MEMORY\_REUSE\_INTERSTAGE);

## メモリ使用量の比較

u2netpでのメモリ使用量の比較です。青がailia SDKのメモリ使用量です。

### デフォルト：全てのテンソルを別メモリに確保

最大メモリ使用量：557.2MB  
getMemoryModeの引数：true,true,false,false

Press enter or click to view image in full size

![]()

通常モード

### Reduce Interstage : テンソルを都度確保・開放

最大メモリ使用量：176.4MB  
getMemoryModeの引数：true,true,true,false

Press enter or click to view image in full size

![]()

Reduce Interstage モード

### Reuse Interstage : 同じサイズのテンソルを再利用

最大メモリ使用量： 296.8MB  
getMemoryModeの引数：true,true,false,true

Press enter or click to view image in full size

![]()

Reuse Interstage モード

## 推論速度の比較

MacBookPro13 (Intel Core i5 2.3GHz Iris Plus Graphics 655)におけるu2netpの推論速度の比較です。5回、推論した場合の各推論時間です。

### デフォルト：全てのテンソルを別メモリに確保

ベースラインとなる推論速度です。1回目の推論ではメモリ確保が行われますが、2回目の推論ではメモリ確保が行われないため高速になります。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

CPU

INFO u2net.py (104) : ailia processing time 269 ms  
INFO u2net.py (104) : ailia processing time 178 ms  
INFO u2net.py (104) : ailia processing time 176 ms  
INFO u2net.py (104) : ailia processing time 177 ms  
INFO u2net.py (104) : ailia processing time 175 ms

GPU

INFO u2net.py (104) : ailia processing time 475 ms  
INFO u2net.py (104) : ailia processing time 153 ms  
INFO u2net.py (104) : ailia processing time 132 ms  
INFO u2net.py (104) : ailia processing time 125 ms  
INFO u2net.py (104) : ailia processing time 122 ms

### Reduce Interstage : テンソルを都度確保・開放

デフォルトモードでは、2回目以降の推論が高速になりますが、Reduce Interstageでは2回目以降も初回実行時と同じ初期化時間が必要になります。また、GPUではメモリの確保と開放のペナルティが大きくなります。

CPU

INFO u2net.py (104) : ailia processing time 268 ms  
INFO u2net.py (104) : ailia processing time 253 ms  
INFO u2net.py (104) : ailia processing time 254 ms  
INFO u2net.py (104) : ailia processing time 255 ms  
INFO u2net.py (104) : ailia processing time 248 ms

GPU

INFO u2net.py (104) : ailia processing time 667 ms  
INFO u2net.py (104) : ailia processing time 627 ms  
INFO u2net.py (104) : ailia processing time 609 ms  
INFO u2net.py (104) : ailia processing time 600 ms  
INFO u2net.py (104) : ailia processing time 644 ms

### Reuse Interstage : 同じサイズのテンソルを再利用

テンソルを共有することでメモリ使用量を抑制するものの、メモリの確保は1回目の推論でしか行わないため、2回目の推論は高速になります。速度とメモリ消費量のバランスの取れたモードとなります。

CPU

INFO u2net.py (104) : ailia processing time 236 ms  
INFO u2net.py (104) : ailia processing time 167 ms  
INFO u2net.py (104) : ailia processing time 171 ms  
INFO u2net.py (104) : ailia processing time 169 ms  
INFO u2net.py (104) : ailia processing time 172 ms

GPU

INFO u2net.py (104) : ailia processing time 461 ms  
INFO u2net.py (104) : ailia processing time 158 ms  
INFO u2net.py (104) : ailia processing time 145 ms  
INFO u2net.py (104) : ailia processing time 139 ms  
INFO u2net.py (104) : ailia processing time 129 ms

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。