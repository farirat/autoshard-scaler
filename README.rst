Kubernetes Discord autosharded bot scaler
-----------------------------------------

This is a K8s StatefulSet autoscaler that uses the Discord's Bot endpoint to get the recommended shards configuration and automatically scale up (or down) the StatefulSet.

This project requires that you already be using Kubernetes, and assume you have some understand of how Kubernetes works.

It also assumes that you have your bot set up to handle changes in the StatefulSet's replica count gracefully.  Meaning: if we scale up, all existing shards will need to re-identify with Discord to present the new shard count, and update their local cache as necessary.

It is also important that your bot accepts the following environment variables:

* **SHARDS**: Total shards running accross all bot instances,
* **SHARD_IDS**: Shard IDs handled by a bot instance, bot-0 must be handling **at least** shard-0,

An example speaks louder than words:

If we have 12 recommended shards and you set **K8S_SHARDS_PER_BOT** to 4 *(default:1)* then we will spin up 4 bots with **SHARDS** =12 and:

* bot-0's **SHARD_IDS** = 0-3
* bot-1's **SHARD_IDS** = 4-7
* bot-2's **SHARD_IDS** = 8-11

Getting Started
===============

* Store your **BOT_TOKEN** in Kubernetes secret, example::

    apiVersion: v1
    kind: Secret
    metadata:
      name: bot-secrets
      namespace: develop
    type: Opaque
    data:
      bot_token: A1fva56Hf7kNakF3TVRVNE1Ut0hOzebiLllpVDJjdy5RYlBfVHlFGjJYZHd4GBM5SldLKJoKYFBHHKL=

* Your bot should be deployed in a statefulset and accepting **SHARDS** and **SHARD_IDS** env variables, example::

    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: bot
      namespace: develop
      labels:
        app: bot
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: bot
      serviceName: "bot"
      template:
        metadata:
          labels:
            app: bot
        spec:
          containers:
            - name: bot
              image: gcr.io/appname/discord-bot:latest
              imagePullPolicy: "Always"
              env:
                - name: BOT_TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: bot-secrets
                      key: bot_token
                - name: SHARDS
                  value: "1"
                - name: SHARDS_PER_BOT
                  value: "1"

* Edit k8s/cronjob.yml and change the environment variables to match your set up
* Apply your cronjob.yml configuration to your cluster and watch the magic !
