import logging.config
import argparse
import yaml
import math
import os
import datetime as dt
import requests
from kubernetes import client, config

logger = logging.getLogger('main')


class Task(object):
    def __init__(self, args):
        logger.info('Initializing task ...')

        # General configuration
        self.args = args

    def run(self):
        try:
            # 1. Get discord's recommended shard count for this bot
            gbot = requests.get('https://discord.com/api/gateway/bot',
                                headers={'Authorization': 'Bot %s' % os.getenv('BOT_TOKEN', '<BOT_TOKEN>')})
            logger.debug('Discord gateway response: %s', gbot.text)
            if gbot.status_code != 200:
               raise Exception("Could not get bot information from discord: %s" % gbot.text)
            recommended_shards = gbot.json()['shards']
            logger.info('Recommended shards: %s', recommended_shards)

            # 2. Get k8s's StatefulSet
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            kcluster = client.AppsV1Api()
            sfs = kcluster.read_namespaced_stateful_set(
                name=os.getenv('K8S_STATEFULSET'), namespace=os.getenv('K8S_NAMESPACE'))

            # 3. What's the recommended_replicas ?
            recommended_replicas = math.ceil(recommended_shards / float(os.getenv('K8S_SHARDS_PER_BOT')))

            # Should scaleup or scaledown ?
            scale = None
            if os.getenv('K8S_SCALEUP') == '1' and int(sfs.spec.replicas) < recommended_replicas:
                logger.info('(Recommended shards: %s) Scaling up replicas from %s to %s ..',
                            recommended_shards, sfs.spec.replicas, recommended_replicas)
                scale = 'UP'
            elif os.getenv('K8S_SCALEDOWN') == '1' and int(sfs.spec.replicas) > recommended_replicas:
                logger.info('(Recommended shards: %s) Scaling down replicas from %s to %s ..',
                            recommended_shards, sfs.spec.replicas, recommended_replicas)
                scale = 'DOWN'

            # Update SHARDS and SHARDS_PER_BOT for each container in the statefulset and schedule it
            # for restarting if required (on change)
            _update_counter = 0
            _restart_required = False
            for _container in sfs.spec.template.spec.containers:
                if _container.name == os.getenv('K8S_CONTAINER'):
                    for _env in _container.env:
                        if _env.name == 'SHARDS_PER_BOT':
                            if _env.value != os.getenv('K8S_SHARDS_PER_BOT'):
                                _restart_required = True
                                logger.info('Setting %s from %s to %s',
                                            _env.name, _env.value, os.getenv('K8S_SHARDS_PER_BOT'))
                                _env.value = os.getenv('K8S_SHARDS_PER_BOT')
                            _update_counter += 1
                        elif _env.name == 'SHARDS':
                            if _env.value != str(recommended_shards):
                                _restart_required = True
                                logger.info('Setting %s from %s to %s',
                                            _env.name, _env.value, str(recommended_shards))
                                _env.value = str(recommended_shards)
                            _update_counter += 1
            if _update_counter != 2:
                raise Exception(
                    "Container with SHARDS_PER_BOT and SHARDS env vars were not found in statefulset %s" %
                    os.getenv('K8S_STATEFULSET'))

            # Scale it (up or down) or just restart the statefulset
            if scale in ['UP', 'DOWN'] or _restart_required:
                logger.info('Patching statefulset %s ..', os.getenv('K8S_STATEFULSET'))

                # Restart remaining pods after scaling
                _now = dt.datetime.utcnow()
                sfs.spec.template.metadata.annotations = {
                    'kubectl.kubernetes.io/restartedAt': str(_now.isoformat("T") + "Z")
                }

                # Update replica count
                sfs.spec.replicas = recommended_replicas
                kcluster.patch_namespaced_stateful_set(
                    name=os.getenv('K8S_STATEFULSET'), namespace=os.getenv('K8S_NAMESPACE'),
                    body=sfs)

        except Exception as e:
            logger.error("Error while running Task (%s): %s", e.__class__.__name__, e)
        else:
            logger.info("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kubernetes Discord autosharded bot scaler')

    args = parser.parse_args()

    try:
        # Logging configuration
        logging.config.dictConfig(yaml.load(open('logging.yml', 'r'), Loader=yaml.SafeLoader))

        # Prepare to start
        task = Task(args)
        task.run()

    except Exception as e:
        print("Error (%s): %s", e.__class__.__name__, e)
    finally:
        pass
