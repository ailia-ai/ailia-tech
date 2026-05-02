---
title: "Contrastive Search : A Token Selection Algorithm That Can Suppress Repetition in Language Generation"
author: "David Cochard"
date: 2023-12-25
lastmod: 2023-12-25
tags: [ailia-technology, machine-learning, ai, nlp]
original_url: https://medium.com/axinc-ai/contrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da
---

# Contrastive Search : A Token Selection Algorithm That Can Suppress Repetition in Language Generation

# Contrastive Search : A Token Selection Algorithm That Can Suppress Repetition in Language Generation

[![David Cochard](../images/contrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da/image_000.jpg)](/@cochard-dav?source=post_page---byline--10712d5408da---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--10712d5408da---------------------------------------)

3 min read

·

Dec 25, 2023

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D10712d5408da&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fcontrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da&source=---header_actions--10712d5408da---------------------post_audio_button------------------)

Share

This article introduces *Contrastive Search*, a token selection algorithm for language generation. It’s an algorithm that resolves the repetition issues of *Greedy Search* and *Beam Search*.

## What is token selection in language generation?

In language generation models, the output of the model’s inference is the probability values of the next token. For instance, in a model with 32,000 types of tokens, probability values for each token are outputted.

From these outputted probability values, the best token is selected using some algorithm, and this selected token is then input back into the model to infer the next token.

By continuously repeating this process, a sequence of tokens is obtained, which is then converted into a string by decoding the sequence with a tokenizer.

## Greedy Search

In *Greedy Search*, the token with the highest probability is selected. While this method is the fastest, it has the problem of often resulting in the repetition of strings.

## Beam Search

*Beam Search*, widely used to suppress the repetition of strings, involves selecting not only the token with the highest probability but also the top-K tokens to create multiple candidates, ultimately choosing the sequence with the highest probability value.

*Beam Search* can yield high-quality output, but is computationally expensive because it requires multiple inferences equal to the number of candidate sequences (beam size).

Furthermore, even with *Beam Search*, the issue with repetitions still persists.

## Contrastive Search

*Contrastive Search* is a method proposed in 2022 that suppresses string repetition by penalizing and making it more difficult to select token sequences that have been output previously. It can suppress repetitions more effectively than *Beam Search* with an equivalent amount of computation.

Press enter or click to view image in full size

![](../images/contrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da/image_001.png)

[## A Contrastive Framework for Neural Text Generation

### Text generation is of great importance to many natural language processing applications. However, maximization-based…

arxiv.org](https://arxiv.org/abs/2202.06417?source=post_page-----10712d5408da---------------------------------------)

To calculate the token `x_t` at time`t`, the selection of `v` from the token candidates `V^k` is determined according to the following evaluation function. The terme `model confidence` is the probability value output by the model, and the model outputs the probability value of the token candidate `v` from the past tokens `x_<​t`. In *Greedy Search*, the output is determined only from this term.

Press enter or click to view image in full size

![](../images/contrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da/image_002.png)

Contrasrtive Search ( Source: <https://arxiv.org/pdf/2202.06417.pdf>)

In *Contrastive Search*, a `degeneration penalty` term is added as a penalty. This penalty is calculated based on the past token sequence `x_j`​ and the current candidate token `v`, and is subtracted from the probability value output by the model.

In this context, `s` represents the cosine distance of the token’s hidden states. For each candidate token `v`, the model’s inference is performed again to obtain its hidden state. An inner product with past hidden states is calculated, and if the candidate token is semantically close to previous tokens, a higher penalty is applied.

![](../images/contrastive-search-a-token-selection-algorithm-that-can-suppress-repetition-in-language-10712d5408da/image_003.png)

Cosine distance ( Source: <https://arxiv.org/pdf/2202.06417.pdf>)

If the model’s inference is performed to calculate the hidden states for all candidates, the computational load becomes significant. Therefore, in practice, the penalty is calculated only for the top-K candidates with the highest probabilities.

`α` is a parameter used to control the penalty. If it is set to 0, the process becomes equivalent to *Greedy Search*.

The actual implementation examples can be found below.

[## Adding State-of-the-art Contrastive Search to the Codebase of model.generate() · Issue #19182 ·…

### Feature request Catalogue: 1. Abstract 2. Introduction 3. Demonstration of the Awesome Results from Contrastive Search…

github.com](https://github.com/huggingface/transformers/issues/19182?source=post_page-----10712d5408da---------------------------------------#code_snippet)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.