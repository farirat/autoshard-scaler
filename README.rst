Kubernetes Discord autosharded bot scaler
-----------------------------------------

This is a K8s StatefulSet autoscaler that uses the Discord's Bot endpoint to get the recommended shards configuration and automatically scale up the StatefulSet.

This project requires that you already be using Kubernetes, and assume you have some understand of how Kubernetes works.

It also assumes that you have your bot set up to handle changes in the StatefulSet's replica count gracefully.  Meaning: if we scale up, all existing shards will need to re-identify with Discord to present the new shard count, and update their local cache as necessary.

It is also important that your bot accepts the following environment variables:

* **SHARDS**: Total shards running accross all bot instances,
* **SHARD_IDS**: Shard IDs handled by a bot instance, bot-0 must be handling **at least** shard-0,

An example speaks louder than words:

If we have 12 recommended shards and you set **scaler_shards_per_bot** to 4 then we will spin up 4 bots with **SHARDS** =12 and:

* bot-0's **SHARD_IDS** = 0-3
* bot-1's **SHARD_IDS** = 4-7
* bot-2's **SHARD_IDS** = 8-11

Getting Started
===============

* Copy config.sample.yml to config.yml and edit it
* ... @TODO
