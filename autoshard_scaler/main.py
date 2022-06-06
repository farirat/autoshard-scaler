import logging.config
import argparse
import yaml

logger = logging.getLogger('main')


class Task(object):
    def __init__(self, args, config):
        logger.info('Initializing task ...')

        # General configuration
        self.config = config
        self.args = args

    def run(self):
        try:
            pass
        except Exception as e:
            logger.error("Error while running Task (%s): %s", e.__class__.__name__, e)
        else:
            logger.info("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kubernetes Discord autosharded bot scaler')
    parser.add_argument('--config', type=str, required=False, default="config.yml",
                        help='Config file')

    args = parser.parse_args()

    try:
        # Load configuration
        config = yaml.load(open(args.config, 'r'), Loader=yaml.SafeLoader)

        # Logging configuration
        logging.config.dictConfig(yaml.load(open(config.get('logging_config'), 'r'), Loader=yaml.SafeLoader))

        # Prepare to start
        task = Task(args, config)
        task.run()

    except Exception as e:
        print("Error (%s): %s", e.__class__.__name__, e)
    finally:
        pass
