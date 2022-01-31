import yaml

if __name__ == '__main__':

    # can be set to be more verbose if a --debug type option is set
    # logging.basicConfig(format='%(message)s', level=logging.INFO)
    try:
        with open('sample-configs/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        file.close()
    except yaml.YAMLError as error:
        raise yaml.YAMLError('There was an error reading config.') from error
