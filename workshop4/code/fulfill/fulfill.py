#!bin/python

import time
from flask import Flask
from flask import request
import json
import requests
import boto3
from urllib2 import urlopen
import logging
import sys


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Get API Key and parameters from SSM
region = urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read().decode('utf-8')
ssmClient = boto3.client('ssm',region_name=region[:-1])

apiKey = ssmClient.get_parameter(Name='/interstella/apiKey')['Parameter']['Value']
endpoint = ssmClient.get_parameter(Name='/interstella/apiEndpoint')['Parameter']['Value']
portNum = 80

def fulfill(apiKey, endpoint, iridium, magnesite):
    if apiKey == '':
        return 'Missing API Key'
    elif endpoint == '':
        return 'Missing endpoint'
    else:
        headers = {'x-api-key': apiKey}
        data = {'iridium': iridium, 'magnesite': magnesite}
        try:
            print 'Trying to send a request to the API'
            response = requests.post(endpoint, headers=headers, data=json.dumps(data))
            if response.status_code == requests.codes.ok:
                print 'API Status Code: '+str(response.status_code)
                return response.status_code
            else:
                response.raise_for_status()
        except Exception as e:
            print e
            response = e
    return response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the fulfillment service"
    
# Fulfillment service
# Expects a POST of {'thing': '1'} from microservice until we separate fulfillment into its own microservice as well
# def fulfill(apiKey, endpoint, spiceMelange, vespene, dilithium, tiberium)
@app.route('/fulfill/', methods=['POST'])
def glueFulfill():
    if request.method == 'POST':
        iridium = 0
        magnesite = 0

        try: 
            # The payload should always be {"item": "1"}. Any other format is wrong, so discard.
            payload = request.get_json(force=True)
            if (len(payload)) != 1:
                print 'Payload incorrectly formatted'
                print 'The data sent was %s' % payload['Message']
                return 'Nothing to fulfill. JSON did not satisfy fulfillment criteria'
            elif 'iridium' in payload:
                iridium = 1
            elif 'magnesite' in payload:
                magnesite = 1
            else: 
                print 'Payload did not include one of the 4 things to fulfill'
                return 'Nothing to fulfill. JSON did not satisfy fulfillment criteria'
            result = fulfill(apiKey, endpoint, iridium, magnesite)
            if result == requests.codes.ok:
                print 'Fulfillment request succeeded'
                return 'Your fulfillment request has been delivered'
            else:
                print 'Fulfillment request failed'
                return 'Your fulfillment request has failed'
        except Exception as e:
            # Looks like it wasn't.
            # print 'Something went wrong with fulfillment. Is the API Online?'
            print e
            return 'Something went wrong with fulfillment. Is the API Online?'
        
        return "Something totally went wrong"
    else:
        # We should never get here
        return "This is not the page you are looking for"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=portNum)
