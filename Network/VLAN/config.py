#!/usr/bin/python36
import json

def get_config(path):
    conf_str = ''
    with open(path) as f:
        for line in f:
            conf_str += line
        conf_dict = json.loads(conf_str)
    return conf_dict