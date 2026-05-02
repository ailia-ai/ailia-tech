---
title: "Bert Network Packet Flow Header Payload: A Machine Learning Model for Detecting Network Attacks"
author: "David Cochard"
date: 2024-08-01
lastmod: 2024-08-01
tags: [ailia-models, machine-learning, ai, bert, network-security]
original_url: https://medium.com/axinc-ai/bert-network-packet-flow-header-payload-a-machine-learning-model-for-detecting-network-attacks-e6fe91cbeae1
---

# Bert Network Packet Flow Header Payload: A Machine Learning Model for Detecting Network Attacks

# Bert Network Packet Flow Header Payload: A Machine Learning Model for Detecting Network Attacks

[![David Cochard](../images/bert-network-packet-flow-header-payload-a-machine-learning-model-for-detecting-network-attacks-e6fe91cbeae1/image_000.jpg)](/@cochard-dav?source=post_page---byline--e6fe91cbeae1---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--e6fe91cbeae1---------------------------------------)

5 min read

·

Aug 1, 2024

--

1

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3De6fe91cbeae1&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fbert-network-packet-flow-header-payload-a-machine-learning-model-for-detecting-network-attacks-e6fe91cbeae1&source=---header_actions--e6fe91cbeae1---------------------post_audio_button------------------)

Share

This is an introduction to「Bert Network Packet Flow Header Payload」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

## Overview

*Bert Network Packet Flow Header Payload* is a machine learning model designed for detecting intrusions in computer networks. It takes the hexadecimal data of packets as input and uses BERT to output tags indicating the type of attack.

[## rdpahalavan/bert-network-packet-flow-header-payload · Hugging Face

### We’re on a journey to advance and democratize artificial intelligence through open source and open science.

huggingface.co](https://huggingface.co/rdpahalavan/bert-network-packet-flow-header-payload?source=post_page-----e6fe91cbeae1---------------------------------------)

The details of Bert Network Packet Flow Header Payload are described in the following paper.

<https://github.com/rdpahalavan/PADEC/blob/main/Thesis/Thesis.pdf>

## The history of network intrusion detection

Network Intrusion Detection Systems (NIDS) detect intrusions by monitoring network traffic. Traditional systems use either signature-based detection, anomaly-based detection, or flow-based detection.

Press enter or click to view image in full size

![](../images/bert-network-packet-flow-header-payload-a-machine-learning-model-for-detecting-network-attacks-e6fe91cbeae1/image_001.png)

Source: <https://github.com/rdpahalavan/PADEC/blob/main/Thesis/Thesis.pdf>

In signature-based detection, attack detection is performed based on known attack patterns. Pattern recognition is performed based on packet information. This method can detect known attack patterns but has the problem of being unable to detect new attack patterns.

In anomaly-based detection, an alert is issued when there is a deviation from the normal state of the network, such as the volume of network traffic, protocol usage, and the state of resources.

Flow-based detection focuses on the network flow during an attack. It uses machine learning models such as RNN and LSTM to detect attacks based on the sequence flow of packets. Transformers have not been used yet.

Datasets such as CIC-IDS2017, UNSW-NB15, CTU-13, and ISCS NSL-KDD can be used for training.

## Architecture

In recent years, Transformer models have emerged. By fine-tuning Transformers for NIDS, it is possible to achieve high-precision detection. This is what Bert Network Packet Flow Header Payload aims to achieve using [BERT](/axinc-ai/bert-a-machine-learning-model-for-efficient-natural-language-processing-aef3081c24e8).

Since the existing BERT is not trained on packet data, fine-tuning is necessary. For compatibility with BERT’s tokenizer, each number in the packet is converted to a string, separated by spaces byte by byte, and concatenated into a long string. The WordPiece tokenizer splits tokens by spaces, making each column of the dataset’s packet an independent token. As BERT’s maximum token length is 512 tokens, the input payload is constrained to a maximum of 500 bytes.

The datasets used are CIC-IDS2017 and UNSW-NB15, which contain packet information. The packet information includes Payload Bytes, Package Bytes, and Packet Fields. 70% of the data is used for training and 30% for validation. The training data consists of 100,000 packets per class, totaling 2.4 million packets. The training classify attacks in the 24 classes below.

```
{'Analysis': 0,  
 'Backdoor': 1,  
 'Bot': 2,  
 'DDoS': 3,  
 'DoS': 4,  
 'DoS GoldenEye': 5,  
 'DoS Hulk': 6,  
 'DoS SlowHTTPTest': 7,  
 'DoS Slowloris': 8,  
 'Exploits': 9,  
 'FTP Patator': 10,  
 'Fuzzers': 11,  
 'Generic': 12,  
 'Heartbleed': 13,  
 'Infiltration': 14,  
 'Normal': 15,  
 'Port Scan': 16,  
 'Reconnaissance': 17,  
 'SSH Patator': 18,  
 'Shellcode': 19,  
 'Web Attack - Brute Force': 20,  
 'Web Attack - SQL Injection': 21,  
 'Web Attack - XSS': 22,  
 'Worms': 23}
```

For inference, the input data is created by extracting meta-information from the packet header hexadecimal data and appending the packet payload.

Press enter or click to view image in full size

![](../images/bert-network-packet-flow-header-payload-a-machine-learning-model-for-detecting-network-attacks-e6fe91cbeae1/image_002.png)

Source: <https://huggingface.co/datasets/rdpahalavan/network-packet-flow-header-payload/blob/main/Data-Format.png>

```
final_format = [  
        forward_packets_per_second,  
        backward_packets_per_second,  
        bytes_transferred_per_second,  
        -1,  
        source_port,  
        destination_port,  
        IP_len,  
        payload_len,  
        IP_ttl,  
        IP_tos,  
        TCP_dataofs,  
        TCP_flags,  
        -1,  
    ]  
 final_format = final_format + payload[:500]
```

Ultimately, the input data will be a string formatted as follows.

```
0 4 5493 -1 443 63834 1480 1428 245 0 8 0 -1 32 87 216 38 19 204 44 114 27 135 158 240 14 109 146 91 202 146 160 45 82 159 213 135 253 142 90 156 185 61 210 164 5 216 49 86 18 80 13 113 121 207 124 1 202 94 24 205 19 127 226 4 79 225 88 152 213 180 39 34 249 231 155 188 116 49 206 113 17 113 170 99 166 183 121 54 125 116 90 11 84 50 250 50 110 142 114 56 209 80 51 218 96 26 75 185 201 190 164 100 ...
```

The tokenizer is applied to this string, which is then input into BERT to obtain the attack type.

## Validation dataset

The data below have been converted for use with Bert Network Packet Flow Header Payload.

[## rdpahalavan/network-packet-flow-header-payload · Datasets at Hugging Face

### We’re on a journey to advance and democratize artificial intelligence through open source and open science.

huggingface.co](https://huggingface.co/datasets/rdpahalavan/network-packet-flow-header-payload?source=post_page-----e6fe91cbeae1---------------------------------------)

## Training on custom data

The fine-tuning code for BERT is provided below. By using this, it is also possible to train on custom data.

[## PADEC/Code/Finetuning\_Models.ipynb at main · rdpahalavan/PADEC

### Thesis research on enhancing Network Intrusion Detection System (NIDS) explainability using Transformers. …

github.com](https://github.com/rdpahalavan/PADEC/blob/main/Code/Finetuning_Models.ipynb?source=post_page-----e6fe91cbeae1---------------------------------------)

The attack classification accuracy on 509,050 test data points appears to be 99.48%

## Usage

*Bert Network Packet Flow Header Payload* can be used with ailia SDK using the command below. The input should be a text file containing the HEX data of the packets. As samples, `input_hex.txt` for a normal packet and `input_exploit.txt` for an attack packet are included.

```
python3 bert-network-packet-flow-header-payload.py --input input_hex.txt
```

[## ailia-models/network\_intrusion\_detection/bert-network-packet-flow-header-payload at master ·…

### The collection of pre-trained, state-of-the-art AI models for ailia SDK …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/network_intrusion_detection/bert-network-packet-flow-header-payload?source=post_page-----e6fe91cbeae1---------------------------------------)

This repository demonstrates the use of *Bert Network Packet Flow Header Payload* for analyzing network traffic. It includes cases where the model is used as-is and cases where it has been fine-tuned to detect DoS attacks on the network, with reports of good results.

The TCP payload is used as input by default according to the official repository, but by using the `-ip` option, it is also possible to store and evaluate the IP packet itself.

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.