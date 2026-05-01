---
title: "TransformersにおけるTokenizerのオプションによる挙動の変化"
author: "Kazuki Kyakuno"
date: 2024-07-31
lastmod: 2024-07-31
original_url: https://tech.ailia.ai/transformersにおけるtokenizerのオプションによる挙動の変化-785d93a37d5f
tags: [ailia-technology]
---

# TransformersにおけるTokenizerのオプションによる挙動の変化

# TransformersにおけるTokenizerのオプションによる挙動の変化

[![Kazuki Kyakuno](../images/transformers____tokenizer______________-785d93a37d5f/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--785d93a37d5f---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--785d93a37d5f---------------------------------------)

21 min read

·

Jul 22, 2024

--

Share

TransformersにおけるTokenizerのオプションによる挙動の変化を解説します。

## Transformersについて

Transformersは各種のTransformerモデルを扱うことのできるライブラリです。Transformersには各種のTokenizerが含まれており、テキストとトークンの相互変換が可能です。

Press enter or click to view image in full size

![](../images/transformers____tokenizer______________-785d93a37d5f/image_001.png)

出典：<https://github.com/huggingface/transformers>

[## GitHub - huggingface/transformers: 🤗 Transformers: State-of-the-art Machine Learning for Pytorch…

### 🤗 Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX. - huggingface/transformers

github.com](https://github.com/huggingface/transformers?source=post_page-----785d93a37d5f---------------------------------------)

## Encodeの呼び出し方法

TransformersでEncodeを行い、テキストをトークンに変換するには、\_\_call\_\_を呼び出します。

```
from transformers import AutoTokenizer  
texts = "This is a test."  
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base')  
outputs = tokenizer(texts)
```

出力例です。input\_idsにトークンIDが、attention\_maskにアテンションマスクが格納されます。アテンションマスクは、各トークンが処理対象かどうかを示します。

```
{'input_ids': [0, 3293, 83, 10, 3034, 5, 2],  
 'attention_mask': [1, 1, 1, 1, 1, 1, 1]}
```

Encodeのデフォルト動作は、padding = False、truncation = False、return\_tensors = None (Pythonのリスト形式) です。

## Encodeのバリエーション

Encodeには、\_\_call\_\_、encode、encode\_plus、batch\_encode\_plusの4種類があります。\_\_call\_\_が最も汎用的で、入力がテキストでもバッチでも処理することができます。

\_\_call\_\_は、strとlist[str]の両方を受けることができます。strが入力されるとencode\_plus、list[str]が入力されるとbatch\_encode\_plusの動作になります。

encodeとencode\_plusはstrを受けることができます。list[str]を受けると、意図しない動作として、special tokensのみが含まれるトークンが出力されます。encodeはinput\_idsのみ出力されます。encode\_plusはinput\_idsに加えて、attention\_maskが出力されます。

batch\_encode\_plusはlist[str]を受けることができます。strを受けると、意図しない動作として、文字単位でバッチ化されます。例えば、textsが”Hello”の場合、[“Hello”]ではなく、[“H”, “e”, “l”, “l”, “o”]がEncodeされます。

## Encodeの推奨オプション

### **最大トークン長を設定して切り詰める場合**

AIモデルに与えられる最大トークン長が規程されており、それを超えないように切り詰めたい場合に使用する設定です。最大トークン長よりも短い場合は、短いトークン長のままになります。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = True, truncation = True, max_length = 77)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2], [0, 35378, 8999, 5, 2, 1, 1]],  
 'attention_mask': [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0]]}
```

padding = Trueとすることで、バッチ入力された場合に、バッチ内の最大のトークン長にパディングされます。また、truncation = Trueとすることで、max\_lengthを超えた場合に、max\_lengthの長さで切り詰められます。

### **必ずmax\_lengthにする場合**

AIモデルに必ず固定長のトークンを与えたい場合に使用する設定です。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = "max_length", truncation = True, max_length = 77)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
 [0, 35378, 8999, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],  
'attention_mask': [[1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
 [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}
```

padding = “max\_length”とすることで、max\_lengthより短い場合にmax\_lengthまでパディングされます。また、truncation = Trueとすることで、max\_lengthを超えた場合に、max\_lengthの長さで切り詰められます。

## Encodeのオプション

### **padding**

パディングを制御します。

**False or “do\_not\_pad”（デフォルト）**：何もしません。バッチ入力された場合、バッチごとに異なるトークン長のトークンが出力されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = False, max_length = 77)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2], [0, 35378, 8999, 5, 2]],  
 'attention_mask': [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]}
```

**True or “longest”**：バッチ入力された場合に、バッチ内の最大のトークン長にパディングします。max\_lengthは無視されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = True, max_length = 77)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2], [0, 35378, 8999, 5, 2, 1, 1]],  
 'attention_mask': [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0]]}
```

**“max\_length”**：max\_lengthよりも短い場合にmax\_lengthまでパディングします。max\_lengthよりも長い場合、何もしません。そのため、出力のトークン長はmax\_lengthを超える場合があります。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = "max_length", max_length = 77)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  
[0, 35378, 8999, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],  
'attention_mask': [[1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
[1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}
```

### truncation

切り詰めを制御します。

**False（デフォルト）**：何もしません。max\_lengthは無視されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, truncation = True, max_length = 4)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2], [0, 35378, 8999, 5, 2]],  
 'attention_mask': [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]}
```

**True**：max\_lengthよりも長い場合に、max\_lengthで切り詰めます。単純な切り取りではなく、切り取った後、最後のトークンとしてEOTトークンを挿入します。下記の例では、切り詰めるだけだと[0, 3293, 83, 10]ですが、切り詰められた後にEOTが挿入されるため、[0, 3293, 83, 2]になります。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, truncation = True, max_length = 4)
```

```
{'input_ids': [[0, 3293, 83, 2], [0, 35378, 8999, 2]],  
 'attention_mask': [[1, 1, 1, 1], [1, 1, 1, 1]]}
```

### return\_tensors

出力形式を制御します。

**None（デフォルト）**：PythonのList形式で出力されます。

テキストを入力するか、テキストのリストを入力するかで、出力の次元数が異なります。

テキストが入力された場合、1次元のListが返されます。

```
texts = "This is a test."  
outputs = tokenizer(texts, return_tensors=None)
```

```
{'input_ids': [0, 3293, 83, 10, 3034, 5, 2],  
 'attention_mask': [1, 1, 1, 1, 1, 1, 1]}
```

テキストのリストが入力された場合、2次元のListが返されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, return_tensors=None)
```

```
{'input_ids': [[0, 3293, 83, 10, 3034, 5, 2], [0, 35378, 8999, 5, 2]],  
 'attention_mask': [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]}
```

**“np”**：numpyのnumpy.array形式で出力されます。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

テキストが入力された場合も、テキストのリストが入力された場合も、2次元のArrayが返されます。

バッチごとに要素数が合わない場合、np.array(np.array(dtype = np.int64), object)が返ります。要素数がバッチ内で変わるために、2次元方向がobjectになっています。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = False, return_tensors = "np")
```

```
{'input_ids': array([array([   0, 3293,   83,   10, 3034,    5,    2]),  
       array([    0, 35378,  8999,     5,     2])], dtype=object),  
 'attention_mask': array([array([1, 1, 1, 1, 1, 1, 1]),  
       array([1, 1, 1, 1, 1])], dtype=object)}
```

全バッチの要素数が合う場合、2次元のnp.arrayが返されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding = True, return_tensors = "np")
```

```
{'input_ids': array([[    0,  3293,    83,    10,  3034,     5,     2],  
       [    0, 35378,  8999,     5,     2,     1,     1]]),  
 'attention_mask': array([[1, 1, 1, 1, 1, 1, 1],  
       [1, 1, 1, 1, 1, 0, 0]])}
```

**“pt”** : torchのtensorの形式で返されます。

テキストが入力された場合も、テキストのリストが入力された場合も、2次元のTensorが返されます。

```
texts = "This is a test."  
outputs = tokenizer(texts, return_tensors="pt")
```

```
{'input_ids': tensor([[   0, 3293,   83,   10, 3034,    5,    2]]),  
 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1]])}
```

padding = Falseでテキストのリストが入力された場合、バッチ単位で要素数を可変にできないため、エラーになります。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, return_tensors="pt")
```

```
ValueError: Unable to create tensor, you should probably activate truncation and/or padding with 'padding=True' 'truncation=True' to have batched tensors with the same length. Perhaps your features (`input_ids` in this case) have excessive nesting (inputs type `list` where type `int` is expected).
```

padding = Trueでテキストのリストが入力された場合、2次元のtensorが返されます。

```
texts = ["This is a test.", "Hello world."]  
outputs = tokenizer(texts, padding=True, return_tensors="pt")
```

```
{'input_ids': tensor([[    0,  3293,    83,    10,  3034,     5,     2],  
        [    0, 35378,  8999,     5,     2,     1,     1]]),  
 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1],  
        [1, 1, 1, 1, 1, 0, 0]])}
```

### text\_pair

textとペアでトークナイズするテキストを与えます。Question + Answerをまとめてトークン化するような場合に使用します。

text\_pairを与えた場合、textとtext\_pairを、それぞれトークンに変換し、結合します。text\_pairのSOTはEOTに置き換えて結合されます。

```
text = ["This is a ", "Hello "]  
text_pair = ["test.", "world."]  
outputs = tokenizer(text, text_pair, padding=True, return_tensors="np")  
decoded = tokenizer.decode(outputs["input_ids"][0])
```

```
{'input_ids': array([[    0,  3293,    83,    10,     2,     2,  3034,     5,     2],  
       [    0, 35378,     2,     2,  8999,     5,     2,     1,     1]]),  
'attention_mask': array([[1, 1, 1, 1, 1, 1, 1, 1, 1],  
       [1, 1, 1, 1, 1, 1, 1, 0, 0]])}  
<s> This is a</s></s> test.</s>
```

text\_pairを使用すると、少し特殊なルールでtruncationが適用されます。truncationのデフォルトは”longest\_first”となっており、textとtext\_pairのうち、max\_lengthに達するまで、1トークンずつ、長い方を削っていきます。textが5トークン、text\_pairが3トークンで、max\_lengthが6トークンの場合、truncation後は、textが3トークン、text\_pairが3トークンになります。

```
text = ["This is a ", "Hello "]  
text_pair = ["test.", "world."]  
outputs = tokenizer(text, text_pair, truncation=True, return_tensors="np", max_length=6)  
decoded = tokenizer.decode(outputs["input_ids"][0])
```

```
{'input_ids': array([[    0,  3293,     2,     2,  3034,     2],  
       [    0, 35378,     2,     2,  8999,     2]]),  
'attention_mask': array([[1, 1, 1, 1, 1, 1],  
       [1, 1, 1, 1, 1, 1]])}  
<s> This</s></s> test</s>
```

truncationに”only\_first”を与えた場合、textのトークンのみ切り詰められます。”only\_second”を与えた場合、text\_pairのトークンのみ切り詰められます。

### **split\_special\_tokens**

テキストにSpecialTokensを含む際に、SpecialTokensをどのように符号化するかを決定します。FastTokenizerではsplit\_special\_tokensを使用できないため、from\_pretrainedにuse\_fast=Falseを指定する必要があります。

**false（デフォルト）**

<s>などのSpecialTokensはSpecialTokenとして符号化されます。

```
sents = "<s>"  
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base', use_fast=False)  
inputs = tokenizer(sents, padding=True, truncation=True, return_tensors='np', split_special_tokens=False)
```

```
{'input_ids': array([[0, 0, 2]]),  
 'attention_mask': array([[1, 1, 1]])}
```

**true**

<s>などのSpecialTokensはテキストとしてトークン化されます。

```
sents = "<s>"  
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base', use_fast=False)  
inputs = tokenizer(sents, padding=True, truncation=True, return_tensors='np', split_special_tokens=True)
```

```
{'input_ids': array([[   0, 4426,    7, 2740,    2]]),  
 'attention_mask': array([[1, 1, 1, 1, 1]])}
```

**特殊条件**

WhisperTokenizerやRobertaTokenizerはsplit\_special\_tokens=Trueが有効に作用しますが、CLIPTokenizerの場合、split\_special\_tokens=Trueが無視され、常にsplit\_special\_tokens=Falseの動作となります。

## Decodeの呼び出し方法

Transformersでデコードを行うには、下記のようにdecodeを呼び出します。デコードを行うことで、トークン列をテキストに変換します。

```
texts = "This is a test."  
outputs = tokenizer(texts)  
texts = tokenizer.decode(outputs["input_ids"])
```

```
<s> This is a test.</s>
```

## Decodeの推奨オプション

### Special Tokensを出力しない

SOT、EOT、PAD、UNKなどのSpecial Tokensを出力しない場合、skip\_special\_tokensにTrueを設定します。

```
texts = "This is a test."  
outputs = tokenizer(texts)  
texts = tokenizer.decode(outputs["input_ids"], skip_special_tokens=True)
```

```
This is a test.
```

### Special Tokensを出力する（デフォルト）

SOT、EOT、PAD、UNKなどのSpecial Tokensを出力する場合、skip\_special\_tokensにFalseを設定します。

```
texts = "This is a test."  
outputs = tokenizer(texts)  
texts = tokenizer.decode(outputs["input_ids"])
```

```
<s> This is a test.</s>
```

## ailia Tokenizerのご紹介

Transformersは非常に便利ですが、Pythonでしか動作しないため、iOSやAndroidアプリへの組み込みが難しいという問題があります。

ax株式会社では、iOSやAndroidでも使用できるTokenizerとして、ailia Tokenizerを提供しています。

C++、Flutter、Unity (C#)、Pythonから使用できるため、アプリにTokenizerを組み込みたい場合は、ぜひ、ご検討ください。

[## ailia Tokenizer : UnityやC++から使用できるNLP向けトークナイザ

### UnityやC++から使用できるNLP向けトークナイザのailia Tokenizerのご紹介です。ailia Tokenizerを使用することで、Python不要で、NLPのトークナイズを行うことが可能です。

medium.com](https://medium.com/axinc/ailia-tokenizer-unity%E3%82%84c-%E3%81%8B%E3%82%89%E4%BD%BF%E7%94%A8%E3%81%A7%E3%81%8D%E3%82%8Bnlp%E5%90%91%E3%81%91%E3%83%88%E3%83%BC%E3%82%AF%E3%83%8A%E3%82%A4%E3%82%B6-b60b68c46b06?source=post_page-----785d93a37d5f---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。