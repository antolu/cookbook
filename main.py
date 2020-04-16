from argparse import ArgumentParser
import logging
from yaml import load, FullLoader
from flask import Flask


log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

app = Flask(__name__)

parser = ArgumentParser()
parser.add_argument('config', help='The YAML file containing the config.', type=str)
args = parser.parse_args()

log.info("Parsed arguments {}".format(args))

with open(args.config, 'r') as f:
    config = load(f, Loader=FullLoader)

