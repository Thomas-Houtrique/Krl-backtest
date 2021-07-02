import os
import json
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def getJsonFromFile(file):
    with open(ROOT_DIR + '/' + file) as json_file:
        return json.load(json_file)
