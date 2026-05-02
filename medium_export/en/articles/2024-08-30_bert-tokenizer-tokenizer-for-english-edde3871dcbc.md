---
title: "BERT Tokenizer: Tokenizer for English"
author: "David Cochard"
date: 2024-08-30
lastmod: 2024-08-30
tags: [ailia-technology, machine-learning, ai, nlp]
original_url: https://medium.com/axinc-ai/bert-tokenizer-tokenizer-for-english-edde3871dcbc
---

# BERT Tokenizer: Tokenizer for English

# BERT Tokenizer: Tokenizer for English

[![David Cochard](../images/bert-tokenizer-tokenizer-for-english-edde3871dcbc/image_000.jpg)](/@cochard-dav?source=post_page---byline--edde3871dcbc---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--edde3871dcbc---------------------------------------)

3 min read

·

Aug 30, 2024

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dedde3871dcbc&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fbert-tokenizer-tokenizer-for-english-edde3871dcbc&source=---header_actions--edde3871dcbc---------------------post_audio_button------------------)

Share

This article presents an overview of the BERT Tokenizer is a tokenizer for English used in the BERT language processing model that we introduced in a [previous blog post](/axinc-ai/bert-a-machine-learning-model-for-efficient-natural-language-processing-aef3081c24e8).

Press enter or click to view image in full size

![](../images/bert-tokenizer-tokenizer-for-english-edde3871dcbc/image_001.png)

Bert (Sesame Street)

## About BERT Tokenizer

The *BERT Tokenizer* is a tokenizer for English used in the [BERT language processing model](/axinc-ai/bert-a-machine-learning-model-for-efficient-natural-language-processing-aef3081c24e8). It takes English text as input and converts it into a sequence of tokens that can be processed by the AI model.

Press enter or click to view image in full size

![](../images/bert-tokenizer-tokenizer-for-english-edde3871dcbc/image_002.png)

Google BERT HuggingFace community

[## google-bert (BERT community)

### This organization is maintained by the transformers team at Hugging Face and contains the historical (pre-"Hub") BERT…

huggingface.co](https://huggingface.co/google-bert?source=post_page-----edde3871dcbc---------------------------------------)

[## transformers/src/transformers/models/bert/tokenization\_bert.py at main · huggingface/transformers

### 🤗 Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX. …

github.com](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/tokenization_bert.py?source=post_page-----edde3871dcbc---------------------------------------)

The *BERT Tokenizer* uses *WordPiece* for subword segmentation. The vocabulary for *WordPiece* is defined below.

[## vocab.txt · google-bert/bert-base-uncased at main

### We’re on a journey to advance and democratize artificial intelligence through open source and open science.

huggingface.co](https://huggingface.co/google-bert/bert-base-uncased/blob/main/vocab.txt?source=post_page-----edde3871dcbc---------------------------------------)

## Algorithm

BERT has two variants: UNCASED and CASED. With the UNCASED version, uppercase and lowercase letters are treated the same, with all text being converted to lowercase. Conversely, with the CASED version letters of different casing are treated differently.

In the BERT Tokenizer, the input string is first split into words using Python’s standard `split` method, using spaces, line breaks, and tabs as delimiters. Additionally, words are also split based on punctuation marks with the Unicode P property (such as !"#$%&'()\*+,-./:;<=>?@[\]^\_`{|}~ ).

For the UNCASED variant, accents are also removed. After converting the text to lowercase using `lower()`, the `_run_strip_accents` method performs Unicode NFD normalization to decompose characters with diacritics. It then removes characters with the Unicode category "Mn" to produce text without accents. When Japanese is input, voicing marks (aka. [dakuten](https://en.wikipedia.org/wiki/Dakuten_and_handakuten)) are also removed, causing characters like "で" to be converted to "て".

Next, words are further split into subwords using *WordPiece*. Subword segmentation is performed using a *greedy longest-match-first* strategy based on the word list defined in the vocabulary.

[## transformers/src/transformers/models/bert/tokenization\_bert.py at main · huggingface/transformers

### 🤗 Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX. …

github.com](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/tokenization_bert.py?source=post_page-----edde3871dcbc---------------------------------------#L361)

## Examples

Let’s take the text `“To be or not to be, that is the question”` as input. It is first split by spaces and punctuation marks into: `[‘to’, ‘be’, ‘or’, ‘not’, ‘to’, ‘be’, ‘,’, ‘that’, ‘is’, ‘the’, ‘question’]`

Next, it is further divided using *WordPiece*, resulting in token IDs `[2000, 2022, 2030, 2025, 2000, 2022, 1010, 2008, 2003, 1996, 3160]`. When decoded, this converts back to the original `“to be or not to be, that is the question”`

## Using the BERT Tokenizer from ailia Tokenizer

Our company offers *ailia Tokenizer*, which can be used on iOS and Android as well since it is available in C++, Flutter, Unity (C#), and Python.

The *BERT Tokenizer* is available starting from *ailia Tokenizer* version 1.3.

[## ailia Tokenizer : NLP Tokenizer for Unity and C++

### Introducing ailia Tokenizer, a tokenizer for NLP that can be used from Unity or C++, without the need for an Python…

medium.com](/axinc-ai/ailia-tokenizer-nlp-tokenizer-for-unity-and-c-e8c3625f9877?source=post_page-----edde3871dcbc---------------------------------------)

[## Released ailia Tokenizer 1.3

### We have released ailia Tokenizer 1.3, which enables mutual conversion between text and tokens. We have also introduced…

medium.com](/axinc-ai/released-ailia-tokenizer-1-3-e24c2068607a?source=post_page-----edde3871dcbc---------------------------------------)

Here is an example of implementing the *BERT Tokenizer* using *ailia Tokenizer* in C++.

```
AILIATokenizer *net;  
ailiaTokenizerCreate(&net, AILIA_TOKENIZER_TYPE_BERT, AILIA_TOKENIZER_FLAG_NONE);  
ailiaTokenizerOpenVocabFile(net, "./test/gen/bert/tokenizer/vocab.txt");  
ailiaTokenizerOpenTokenizerConfigFile(net, "./test/gen/bert/tokenizer/tokenizer_config.json");  
ailiaTokenizerEncode(net, u8"To be or not to be, that is the question");  
unsigned int count;  
ailiaTokenizerGetTokenCount(net, &count);  
std::vector<int> tokens(count);  
ailiaTokenizerGetTokens(net, &tokens[0], count);  
ailiaTokenizerDestroy(net);
```

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.