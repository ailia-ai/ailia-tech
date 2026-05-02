---
title: "Prompt Engineering in Whisper"
author: "David Cochard"
date: 2023-11-21
lastmod: 2023-11-21
tags: [ailia-technology, machine-learning, ai, speech-recognition, whisper]
original_url: https://medium.com/axinc-ai/prompt-engineering-in-whisper-6bb18003562d
---

# Prompt Engineering in Whisper

# Prompt Engineering in Whisper

[![David Cochard](../images/prompt-engineering-in-whisper-6bb18003562d/image_000.jpg)](/@cochard-dav?source=post_page---byline--6bb18003562d---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--6bb18003562d---------------------------------------)

3 min read

·

Nov 21, 2023

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D6bb18003562d&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fprompt-engineering-in-whisper-6bb18003562d&source=---header_actions--6bb18003562d---------------------post_audio_button------------------)

Share

*Whisper*, an AI model for speech recognition also uses a language model internally, therefore we can apply some prompt engineering concepts to improve the recognition accuracy of unknown words.

---

## Whisper Overview

*Whisper* is a speech recognition model developed by *OpenAI*, the company behind *ChatGPT*. *Whisper* converts the input speech into a feature vector and generates text based on this feature vector one character at a time in a language model. It was described in details in the following article.

[## Whisper : Speech recognition model capable of recognizing 99 languages

### This is an introduction to「Whisper」, a machine learning model that can be used with ailia SDK. You can easily use this…

medium.com](/axinc-ai/whisper-speech-recognition-model-capable-of-recognizing-99-languages-5b5cf0197c16?source=post_page-----6bb18003562d---------------------------------------)

Prompt engineering has been the focus of much attention recently with the success of *ChatGPT.* Let’s see how this concept can be applied to *Whisper*.

## Prompt Engineering

*Whisper* uses the concepts of *prompt* and *prefix* as it is mentioned for example in this github discussion.

[## prompt vs prefix in DecodingOptions · openai/whisper · Discussion #117

### You can’t perform that action at this time. You signed in with another tab or window. You signed out in another tab or…

github.com](https://github.com/openai/whisper/discussions/117?source=post_page-----6bb18003562d---------------------------------------#discussioncomment-3727051)

Here the *prompt* is a sequence of tokens given as prior information, typically a sequence of tokens decoded in the audio segment preceding the one currently being processed. Its goal is to keep a consistent output between segments by keeping track of previously transcribed information.

The *prefix* is a sequence of tokens representing a partial transcription for the current audio input, allowing for resuming the transcription after a certain point within the 30-second speech. The *prefix* is for example used for real-time transcription of live audio.

Press enter or click to view image in full size

![](../images/prompt-engineering-in-whisper-6bb18003562d/image_001.png)

Concepts of prompt and prefix in Whisper (Source: <https://github.com/openai/whisper/discussions/117#discussioncomment-3727051>)

In the official *Whisper* implementation, a prompt can be given as input via the `initial_prompt` string argument. It is possible to customize *Whisper* by embedding non-textual information from one previous audio segment in this prompt.

## Applications of Custom Prompts

A useful use of custom prompt is to improve the recognition unknown words such as of people’s names and technical terms.

Another interesting use case of custom prompts is to clearly mark the change of speaker by an hyphen in a transcribed conversation. This can be done using the following initial prompt, where an hyphen is inserted between the question and its answer, however is does not work for all languages.

```
initial_prompt="- How are you? - I'm fine, thank you."
```

## Prompt Constraints

The size of the context in *Whisper* is 448, which represents the total number of tokens for input and output, but the official *Whisper* implementation is constrained to half the number of tokens for input, up to 224 tokens. If your custom prompt needs to be larger, for example if your transcription contains a lot of unknown words, then other methods have to be used.

We mentioned the `initial_prompt` parameter earlier that can be used to give a custom prompt. However this will only be used in the first 30 seconds speech, because in the next segment the prompt is overwritten by the decoding result of the current segment.

As suggested in the github discussion below, the [ailia MODELS implementation](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/whisper) applies the prompt argument to segments other than the first, so it is possible to keep the custom prompt across segments.

[## add always\_use\_initial\_prompt by mercury233 · Pull Request #1040 · openai/whisper

### Add this suggestion to a batch that can be applied as a single commit. This suggestion is invalid because no changes…

github.com](https://github.com/openai/whisper/pull/1040?source=post_page-----6bb18003562d---------------------------------------)

Below is an usage example of prompts with ailia MODELS.

```
python3 whisper.py -i recording.m4a --prompt "openai chatgpt"
```

[## ailia-models/audio\_processing/whisper at master · axinc-ai/ailia-models

### Audio file Recognized speech text He hoped there would be stew for dinner, turnips and carrots and bruised potatoes and…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/whisper?source=post_page-----6bb18003562d---------------------------------------)

## About ailia Speech

[ax Inc.](https://axinc.jp/en/) provides a library that allows AI speech recognition using *Whisper* to run offline as a Unity or C++ API, including custom prompt features.

[## ailia AI Speech : Speech Recognition Library for Unity and C++

### Introducing ailia AI Speech, an AI speech recognition library which allows you to easily implement speech recognition…

medium.com](/axinc-ai/ailia-ai-speech-speech-recognition-library-for-unity-and-c-d29db1abe978?source=post_page-----6bb18003562d---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.