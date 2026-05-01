---
title: "AWSのGPUインスタンスにailia SDKをデプロイする"
author: "Kazuki Kyakuno"
date: 2023-12-15
original_url: https://tech.ailia.ai/awsのgpuインスタンスにailia-sdkをデプロイする-cdf5b83675cd
---

# AWSのGPUインスタンスにailia SDKをデプロイする

# AWSのGPUインスタンスにailia SDKをデプロイする

[![Kazuki Kyakuno](../images/aws_gpu_______ailia-sdk_______-cdf5b83675cd/image_000.png)](https://kyakuno.medium.com/?source=post_page---byline--cdf5b83675cd---------------------------------------)

[Kazuki Kyakuno](https://kyakuno.medium.com/?source=post_page---byline--cdf5b83675cd---------------------------------------)

20 min read

·

Dec 15, 2023

--

Share

AWSのGPUインスタンスにailia SDKをデプロイする方法を解説します。ailia SDKとailia MODELSを使用することで、様々なAIモデルをAWS上で実行することが可能です。

## ailia SDKについて

ailia SDKはクロスプラットフォームの推論エンジンです。CPUとGPUを使用した高速推論が可能であり、環境に応じて最適な方法でAIを推論可能です。ailia SDKを使用することで、macOSではMetalを使用して開発しつつ、AWSのEC2ではNVIDIAのcuDNNを使用して高速推論することが可能です。ailia SDKは依存するライブラリが少ないため、Docker Imageに含めるだけで使用可能です。

Press enter or click to view image in full size

![]()

ailia SDK (<https://axinc.jp/solutions/ailia_sdk.html>)

## 今回構築するもの

AWS上にailia SDKを搭載したGPUインスタンスを構築します。ネットワーク構成は下記となります。

```
インターネットゲートウェイ  
-> ロードバランサ (リスナーとルール)  
-> EC2のターゲットグループ  
-> EC2のインスタンス
```

## Dockerについて

Dockerはコンテナ型の仮想環境です。構成ファイルであるDockerfileから、Docker Imageをビルドし、コンテナリポジトリにDocker Imageをプッシュすることで、任意の環境で同じプログラムを実行可能となります。

```
開発PC  
Dockerfile -> [docker build] -> Docker Image -> [docker push]  
  
EC2  
[docker pull] -> [docker run]
```

## EC2インスタンスの作成

EC2（Elastic Compute Cloud）はAWS上の仮想サーバです。AMI（Amazonマシンイメージ）というOSを含む初期イメージを指定して起動します。

今回は、GPUを使用するため、Amazon Deeplearning AMIを指定してEC2インスタンスを作成します。Amazon Deeplearning AMIにはNVIDIAドライバとNVIDIA Dockerが含まれています。自分でNVIDIAドライバとNVIDIA Dockerをインストールするのは大変ですが、Amazon Deeplearning AMIを使用することで、簡単にセットアップが可能です。

Press enter or click to view image in full size

![]()

EC2のインスタンスタイプには、NVIDIAのGPUを搭載したg4dn.xlargeを指定します。g4dnはAWS上では最も安価なGPUインスタンスです。オンデマンド料金は0.526 USD/時間で、月額で$378.72になります。NVIDIA T4 GPUを搭載しています。

[## Amazon EC2 G4 インスタンス - アマゾン ウェブ サービス (AWS)

### 機械学習の推論とグラフィックを多用するアプリケーション向けの、業界で最も費用対効果の高い GPU インスタンス Amazon EC2 G4…

aws.amazon.com](https://aws.amazon.com/jp/ec2/instance-types/g4/?source=post_page-----cdf5b83675cd---------------------------------------)

[## 推論を活用するための NVIDIA T4 Tensor コア GPU

### NVIDIA Turing Tensor コアを搭載した NVIDIA T4 は、現代 AI のさまざまなアプリケーションを加速する画期的な多精度の推論パフォーマンスを提供します。

www.nvidia.com](https://www.nvidia.com/ja-jp/data-center/tesla-t4/?source=post_page-----cdf5b83675cd---------------------------------------)

インスタンス作成時に、sshのログインに使用するキーペアと、インスタンスを立ち上げるVPC（Virtual Private Cloud）とサブネット、パブリックIPの自動割り当てを設定します。なお、これらの設定はインスタンス作成時に有効にしないと、変更はできないため注意してください。

Press enter or click to view image in full size

![]()

## Docker Imageにailia SDKを含める

次に、EC2のインスタンス上で動かすDocker ImageをローカルPCで作成します。

Docker Imageにailia SDKを含めるため、ailia SDKのpython/ailiaをプロジェクトフォルダにコピーします。python/ailiaフォルダの中に、EC2向けのlibrary/linux/\*.soと、開発環境向けにlibrary/mac/\*dylibやlibrary/windows/x64/\*.dllをコピーします。

これで、main.pyからimport ailiaを行い、ailia SDKを使用することが可能です。

Press enter or click to view image in full size

![]()

プロジェクト構成

DockerのBase Imageとして、FROMにNVIDIAのImageを指定します。使用できるImageのリストは下記にあります。必ず、cudnnを含んだImageを使用する必要があります。

[## doc/supported-tags.md · master · nvidia / container-images / cuda · GitLab

### GitLab.com

gitlab.com](https://gitlab.com/nvidia/container-images/cuda/blob/master/doc/supported-tags.md?source=post_page-----cdf5b83675cd---------------------------------------)

今回は、nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04を使用します。このImageには、cudaとcuDNNが含まれています。

macOSのArm環境でビルドする場合、platformに明示的にlinux/amd64を指定します。Arm環境でビルドすると、Arm向けのImageができてしまい、EC2のx86のインスタンスで実行できなくなるためです。

```
FROM --platform=linux/amd64 nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04  
  
RUN apt-get -y update && apt-get -y install python3 python3-pip  
  
RUN mkdir -p /usr/share/app  
WORKDIR /usr/share/app  
  
COPY requirements.txt .  
RUN pip3 install -r requirements.txt  
  
COPY *.py ./  
COPY ailia/ ailia/  
RUN find . -type f -exec chmod 644 {} +  
  
ENTRYPOINT gunicorn --bind 0.0.0.0:8080 main:app  
EXPOSE 8080/tcp
```

DockerfileにCOPY ailiaを追加します。これで、Docker Imageにailiaのバイナリが含まれます。

今回はFlaskでWEBサーバを構築するため、requirements.txtは下記のようになります。gunicornはNGINXとFlaskを繋ぐためのインタフェースで、WEBサーバの起動を行ってくれます。

```
WebOb  
Paste  
grpcio  
Flask==2.2.5  
unstructured  
gunicorn  
numpy  
opencv-python  
pillow  
scikit-image  
ftfy
```

DockerfileからDocker Imageをビルドします。

```
docker build -t ailia-test .
```

使用していないDocker Imageを削除します。

```
docker image prune -f
```

ローカル環境でDocker Imageをテストします。

```
docker run -it --rm --name ailia-test --publish 8080:8080/tcp ailia-test
```

## Docker ImageのECRへのPush

EC2からDocker Imageをダウンロードできるように、AmazonのECR（ Elastic Container Registry）にDocker ImageをPushします。ECRはコンテナリポジトリで、コンテナ向けのgithubのような役割となります。

## Get Kazuki Kyakuno’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

awsコマンドがバージョン1の場合は、SSOが使用できないため、バージョン2にアップデートします。バージョン1の場合は、下記のようなメッセージが表示されます。

```
Note: AWS CLI version 2, the latest major version of the AWS CLI, is now stable and recommended for general use. For more information, see the AWS CLI version 2
```

[公式の手順](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/getting-started-install.html)だと、なぜかシンボリックリンクが作成されないため、手動でシンボリックリンクを作成します。

```
sudo yum remove awscli  
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"  
unzip awscliv2.zip  
sudo ./aws/install  
sudo ./aws/install —update  
sudo ln -s /usr/local/aws-cli/v2/2.15.0/bin/aws /usr/bin/aws
```

EC2にSSO（Single Sign On）で認証情報を取得します。このコマンドで、一定時間、ECRへのアクセス権限が付与されます。コマンドを実行すると、AWSのstart URLが求められるので、https://d-xxx.awsapps.com/start/のようなstart URLを設定します。そうすると、ブラウザが開き、認証を行うことができます。

```
aws configure sso
```

ECRにDocker ImageをPUSHします。SSO\_PROFILEには、ssoコマンドの戻り値のプロファイル名を指定します。

```
export AILIA_SSO_PROFILE="AdministratorAccess-xxx"  
export AILIA_ECR_URI="xxx.dkr.ecr.ap-northeast-1.amazonaws.com"  
  
aws ecr get-login-password --profile ${AILIA_SSO_PROFILE} --region ap-northeast-1 | docker login --username AWS --password-stdin ${AILIA_ECR_URI}  
docker tag ailia-test:latest ${AILIA_ECR_URI}/ailia-test:latest  
docker push ${AILIA_ECR_URI}/ailia-testlatest
```

## EC2でのプルと実行

EC2にログインします。接続先はEC2のグローバルIPアドレスとなります。認証にはインスタンス作成時に使用したキーペアを使用します。

```
ssh -i "../your_key.pem" ec2-user@${IP_ADDR}
```

SSOで認証情報を取得します。

```
aws configure sso
```

ECRからdocker pullを行い、Docker Imageをダウンロードします。

```
export AILIA_SSO_PROFILE="AdministratorAccess-xxx"  
export AILIA_ECR_URI="xxx.dkr.ecr.ap-northeast-1.amazonaws.com"  
  
aws ecr get-login-password --region ap-northeast-1 --profile ${AILIA_SSO_PROFILE} | docker login --username AWS --password-stdin ${AILIA_ECR_URI}  
docker pull ${AILIA_ECR_URI}/ailia-test:latest  
docker tag ${AILIA_ECR_URI}/ailia-test ailia-test
```

docker runを行う際に、 — gpus allコマンドを付与します。このコマンドを付与することで、GPUが有効になります。また、 — restart alywaysを付与することで、再起動後に自動的にコンテナが立ち上がります。

```
docker run --gpus all--restart always --detach --name ailia-test --publish 8080:8080/tcp ailia-test
```

## ログの接続

WEBサーバのログを確認したい場合、AWSのCloud Watchにログを接続します。Cloud Watchにログを接続するには、docker runに — log-driverを指定します。

```
docker run --gpus all--restart always --detach --name ailia-test --publish 8080:8080/tcp --log-driver=awslogs --log-opt awslogs-region=ap-northeast-1 --log-opt awslogs-group=ailia-test-log ailia-test
```

Cloud Watchを使用するには、EC2インスタンスのIAM Roleに CloudWatchAgentServerRoleを設定している必要があります。

![]()

IAMロールの設定

適切にロールが設定されていない場合、下記のエラーになります。

```
docker: Error response from daemon: failed to initialize logging driver: failed to create Cloudwatch log stream: NoCredentialProviders: no valid providers in chain. Deprecated.  
 For verbose messaging see aws.Config.CredentialsChainVerboseErrors.
```

以上で、EC2のコンソールのCloud Watchのロググループからログを確認可能になります。

![]()

ロググループ

また、メモリ使用量とディスク使用量をモニタリングしたい場合、CloudWatchAgentをインストールする必要があります。Amazon Linux 2013にはデフォルトでCloudWatchAgentがインストールされているため、下記のコマンドで設定ファイルの作成を行います。

```
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

「Do you want to specify any additional log files to monitor?」と「Do you want to store the config in the SSM parameter store?」だけデフォルト値ではなくnoにします。

collectdをインストールします。

```
sudo amazon-linux-extras install collectd
```

下記のコマンドでCloudWatchを起動します。

```
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
```

CloudWatchの全てのメトリクスのCWAgentで参照できるようになります。

Press enter or click to view image in full size

![]()

ログは、Pythonのloggerを使用して発行します。

```
logger.info("info test")  
logger.warning("warning test")  
logger.error("error test")
```

## NVIDIAのイメージの内容

これまでの手順で、EC2上でailiaが使用できるようになりました。ここからは、実際に、どのようなライブラリが入っているかを確認してみます。

EC2にsshでログイン後、nvidia-smiでNVIDIAのドライバがインストールされているかが確認できます。

```
nvidia-smi
```

起動しているDocker Imageの中に入ります。

```
docker exec -it ailia-test /bin/bash
```

lddコマンドでlibailia\_cuda-8.8.soの依存ライブラリを調べると、/usr/lib/x86\_64-linux-gnuにcudnnが、/usr/local/cuda/targets/x86\_64-linux/libにcudaが入っていることがわかります。

```
/usr/share/app/ailia# ldd libailia_cuda-8.8.so  
 linux-vdso.so.1 (0x00007ffff9fdd000)  
 libdl.so.2 => /usr/lib/x86_64-linux-gnu/libdl.so.2 (0x00007fc07d0e2000)  
 librt.so.1 => /usr/lib/x86_64-linux-gnu/librt.so.1 (0x00007fc07d0dd000)  
 libcudnn_cnn_infer.so.8 => /usr/lib/x86_64-linux-gnu/libcudnn_cnn_infer.so.8 (0x00007fc059e00000)  
 libcudnn_ops_infer.so.8 => /usr/lib/x86_64-linux-gnu/libcudnn_ops_infer.so.8 (0x00007fc054400000)  
 libcudnn_ops_train.so.8 => /usr/lib/x86_64-linux-gnu/libcudnn_ops_train.so.8 (0x00007fc04fe00000)  
 libcudart.so.12 => /usr/local/cuda/targets/x86_64-linux/lib/libcudart.so.12 (0x00007fc04fa00000)  
 libcublas.so.12 => /usr/local/cuda/targets/x86_64-linux/lib/libcublas.so.12 (0x00007fc049200000)  
 libcublasLt.so.12 => /usr/local/cuda/targets/x86_64-linux/lib/libcublasLt.so.12 (0x00007fc026200000)  
 libm.so.6 => /usr/lib/x86_64-linux-gnu/libm.so.6 (0x00007fc07cff4000)  
 libpthread.so.0 => /usr/lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fc07cfef000)  
 libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fc025fd4000)  
 libgcc_s.so.1 => /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fc07cfcd000)  
 libc.so.6 => /usr/lib/x86_64-linux-gnu/libc.so.6 (0x00007fc025dac000)  
 /lib64/ld-linux-x86-64.so.2 (0x00007fc07d0f4000)  
 libz.so.1 => /usr/lib/x86_64-linux-gnu/libz.so.1 (0x00007fc07cfb1000)
```

## Intel環境での利用

NVIDIAのcuDNNとCUDAを含んだDocker ImageはIntel環境でも動作するため、そのままデプロイすることが可能です。ただし、NVIDIAのImageは通常のUbuntuのImageよりも20GB程度大きいため、イメージサイズを小さくしたい場合は、通常のUbuntuのImageを使用してください。CPU推論になりますが、ailia SDKは通常のUbuntuのImageでも問題なく動作します。

```
FROM --platform=linux/amd64 ubuntu:22.04
```

## まとめ

AWSのGPUインスタンスにailia SDKをデプロイすることで、300種類以上の豊富なモデルライブラリが利用可能になります。ぜひ、ご利用ください。

[## GitHub - axinc-ai/ailia-models: The collection of pre-trained, state-of-the-art AI models for ailia…

### The collection of pre-trained, state-of-the-art AI models for ailia SDK - GitHub - axinc-ai/ailia-models: The…

github.com](https://github.com/axinc-ai/ailia-models?source=post_page-----cdf5b83675cd---------------------------------------)

## 参考文献

EC2におけるGPUインスタンスの作成について

[## AWS EC2でDeepStreamやCUDA対応のOpenCVを利用する方法

### AWS EC2でDeepStreamやCUDA，CUDA対応のOpenCVなどGPU系の処理を行う場合の環境構築方法を備忘録としてまとめます。

www.smarthome-diy.info](https://www.smarthome-diy.info/blog/developper/smarthome/2021/01/2772/?source=post_page-----cdf5b83675cd---------------------------------------)

CloudWatchへの接続について

[## CloudWatch エージェントの構築 - Qiita

### はじめに本記事はAWS環境においてCloudWatch エージェントを導入し、EC2及びECSに対してサーバ監視を行うための方法について記載しています。CloudWatchはAWS環境におけるモ...

qiita.com](https://qiita.com/Brutus/items/b07df93ebfa4a56f6bd8?source=post_page-----cdf5b83675cd---------------------------------------)

エラーログからの通知について

[## 【AWS】CloudWatchでログ監視し、アラーム状態となったらメール送信を行う - Qiita

### ■はじめにCloudWatch、SNSトピックを利用してログに特定文字列が出力されたらアラーム発報し、メールを送信するところまで試しに構築してみたので手順をまとめました。#■対象者本記事はA...

qiita.com](https://qiita.com/CycleSHD/items/703a62c8faa0b9aaa4f8?source=post_page-----cdf5b83675cd---------------------------------------)

ax株式会社はAIを実用化する会社として、クロスプラットフォームでGPUを使用した高速な推論を行うことができるailia SDKを開発しています。ax株式会社ではコンサルティングからモデル作成、SDKの提供、AIを利用したアプリ・システム開発、サポートまで、 AIに関するトータルソリューションを提供していますのでお気軽に[お問い合わせ](https://axinc.jp/)ください。