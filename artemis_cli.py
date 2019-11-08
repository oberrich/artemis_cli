#!/usr/bin/env python

# pip install pyyaml argparse requests json
import yaml
import argparse

from detail.artemis_api import ArtemisAPI

parser = argparse.ArgumentParser(description='A command-line application for tutors to more productively grade programming excises on ArTEMiS')
# TODO: think of and parse arguments
args = parser.parse_args();

with open('config.yml', 'r') as config_file:
    cfg = yaml.safe_load(config_file)

api = ArtemisAPI(cfg['artemis'])

# TODO implement API in detail/artemis_api.py
