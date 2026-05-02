---
title: "DeepSort : A Machine Learning Model for Tracking People"
author: "David Cochard"
date: 2021-05-12
lastmod: 2021-05-12
tags: [ailia-models, machine-learning, deep-learning, ai, object-detection]
original_url: https://medium.com/axinc-ai/deepsort-a-machine-learning-model-for-tracking-people-1170743b5984
---

# DeepSort : A Machine Learning Model for Tracking People

# DeepSort : A Machine Learning Model for Tracking People

[![David Cochard](../images/deepsort-a-machine-learning-model-for-tracking-people-1170743b5984/image_000.jpg)](/@cochard-dav?source=post_page---byline--1170743b5984---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--1170743b5984---------------------------------------)

5 min read

·

May 12, 2021

--

2

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D1170743b5984&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fdeepsort-a-machine-learning-model-for-tracking-people-1170743b5984&source=---header_actions--1170743b5984---------------------post_audio_button------------------)

Share

This is an introduction to「DeepSort」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*DeepSort* is a machine learning model for tracking people, assigning IDs to each person.

Press enter or click to view image in full size

![](../images/deepsort-a-machine-learning-model-for-tracking-people-1170743b5984/image_001.gif)

Test video：TownCentreXVID（<http://www.robots.ox.ac.uk/~lav/Research/Projects/2009bbenfold_headpose/project.html>）

[## Simple Online and Realtime Tracking with a Deep Association Metric

### Simple Online and Realtime Tracking (SORT) is a pragmatic approach to multiple object tracking with a focus on simple…

arxiv.org](https://arxiv.org/abs/1703.07402?source=post_page-----1170743b5984---------------------------------------)

Traditionally, tracking has used an algorithm called *Sort (Simple Online and Realtime Tracking)*, which uses the Kalman filter. Using the bounding boxes detected by [YOLO v3](/axinc-ai/yolov3-a-machine-learning-model-to-detect-the-position-and-type-of-an-object-60f1c18f8107), we can assign an ID and track a person by mapping bounding boxes of similar size and similar motion in previous and following frame.

However, *Sort* presents the limitation that if a person hid behind an object and then reappeared, it is assigned a different ID. *DeepSort* solves this problem by using an AI model that compares similarity between people, thus reducing the issue of switching people’s identities.

## Architecture

In *DeepSort*, the process is as follows.

1. Compute bounding boxes using [YOLO v3](/axinc-ai/yolov3-a-machine-learning-model-to-detect-the-position-and-type-of-an-object-60f1c18f8107) (*detections*)
2. Use *Sort* (Kalman filter)and *ReID* (identification model) to link bounding boxes and *tracks*
3. If no link can be made, a new ID is assigned and it is newly added to *tracks*.

What is referred as “*detections”* is the list of people in one frame, and *“tracks”* is the list of people currently being tracked. Each item of *tracks* is assigned an ID, and by assigning a bounding box to each one of those items, you can assign an ID to the person.

*ReID* is mainly used when linking bounding boxes and tracks. The distance between the feature vectors computed by *ReID* from the person image of the current tracking target (tracks) and the feature vectors also calculated by *ReID* from the person image cut out by the bounding box (detections) in YOLO v3, is used to link bounding boxes and tracks. Simply put, the object with the smallest distance is considered to be the same person and assigned a track ID. To calculate the vector distance, feature vectors for the last 100 frames for each track are used. At this time, the coordinate information of the track is not taken into account.

The cost function is defined as `Sort distance * λ + ReID distance`, but in the paper, λ = 0 turned out to empirically give good results, so the coordinate information is not taken into account.

> During our experiments we found that setting λ = 0 is a reasonable choice when there is substantial camera motion. In this setting, only appearance information are used in the association cost term. However, the Mahalanobis gate is still used to disregarded infeasible assignments based on possible object locations inferred by the Kalman filter.

If the position in the current frame, which is assumed based on the *Sort* past tracking information, is too far apart, the ID will not be assigned. When a bounding box is left without any ID, *Sort* is used to to assign one.

If the bounding box is “lost” for 70 frames, it will be removed from the tracking.

The *ReID* model is trained from 1,100,000 images of 1,261 pedestrians from the *large-scale person re-identification dataset*.

## DeepSort instance creation

DeepSort can be instantiated as follows.

> MAX\_COSINE\_DISTANCE = 0.2 # threshold of matching object  
> NN\_BUDGET = 100
>
> # tracker class instance  
> metric = NearestNeighborDistanceMetric(  
> “cosine”, MAX\_COSINE\_DISTANCE, NN\_BUDGET  
> )
>
> tracker = Tracker(  
> metric,  
> max\_iou\_distance=0.7,  
> max\_age=70,  
> n\_init=3  
> )

`MAX_COSINE_DISTANCE` is a threshold to determine the person similarity by ReID. The higher the value, the easier it is to assume it is the same person.

`NN_BUDGET` is a value that indicates how many previous frames of feature vectors should be retained for distance calculation for each track.

The `max_age` parameter of the tracker specifies after how many frames unallocated tracks will be deleted. `n_init` specifies after how many frames newly allocated tracks will be activated. `max_iou_distance` is a threshold value that determines how much the bounding boxes should overlap to determine the identity of the unassigned track.

> # update tracker  
> tracker.predict()  
> tracker.update(detections)

In the source code, specifically in`sort/tracker.py` , when the `update` function is executed, `_match` is called, and `linear_assignment.matching_cascade`, which uses *Sort* and *ReID*, and `linear_assignment. min_cost_matching` are also called in that order.

In `linear_assignment.matching_cascade`, `min_cost_matching` is called, distance calculation is done by *ReID*, and cost matrix of *detections* N and *tracks* M is calculated. Here, the cost is calculated from the features only, without considering the coordinate information.

After that, in `distance_metric`, the distance calculation of *Sort* is performed by calling `gating_distance` for the cost matrix that has been calculated by *ReID*, and if the distance of *Sort* is greater than a certain value, the cost value *Infinity* is assigned.

Finally, by associating the ID with the lowest cost among the cost matrixes, we can associate the track with the detection that has the closest *ReID* distance with a *Sort* distance below a certain level.

> gated\_cost=INFTY\_COST  
> cost\_matrix[row, gating\_distance > gating\_threshold] = gated\_cost  
> （sort/libnear\_assignment.py/gate\_cost\_matrix）

## DeepSort benchmark

DeepSort has been evaluated on the *MOT Challenge* data set.

[## MOT Challenge

### We have created a framework for the fair evaluation of multiple people tracking algorithms. In this framework we…

motchallenge.net](https://motchallenge.net/?source=post_page-----1170743b5984---------------------------------------)

Press enter or click to view image in full size

![](../images/deepsort-a-machine-learning-model-for-tracking-people-1170743b5984/image_002.png)

(Source：<https://arxiv.org/abs/1703.07402>)

Compared to simple SORT, the switching of person IDs improves from 1423 to 781.

## Usage

To use DeepSort with the ailia SDK, use the sample below.

[## axinc-ai/ailia-models

### DeepSORT original mode: compare image mode: [‘correct\_32\_1.jpg’ , ‘correct\_32\_2.jpg’ ]: SAME person (confidence…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_tracking/deepsort?source=post_page-----1170743b5984---------------------------------------)

In this sample, *DeepSort* is used to track a person detected by YOLOv3. You can use the following command to track against the web camera.

```
$ python3 deepsort.py -v 0
```

You can also calculate the similarity of a person by giving it two still images.

```
$ python3 deepsort.py — pairimage IMAGE_PATH1 IMAGE_PATH2
```

Note that *scipy* is required since it is used to calculate the Kalman filter.

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.