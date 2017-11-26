#!bin/python

import time
from flask import Flask
from flask import request
import json
import requests
import boto3
from urllib2 import urlopen

# Get API Key and parameters from SSM
region = urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read().decode('utf-8')
ssmClient = boto3.client('ssm',region_name=region[:-1])

apiKey = ssmClient.get_parameter(Name='/interstella/apiKey')['Parameter']['Value']
endpoint = ssmClient.get_parameter(Name='/interstella/apiEndpoint')['Parameter']['Value']
orderTopic = ssmClient.get_parameter(Name='/interstella/orderTopic')['Parameter']['Value']
orderTopicRegion = orderTopic.split(':')[3]
portNum = 5000

# Subscribe SNS
'''
snsClient = boto3.client('sns',region_name=orderTopicRegion)
ip = urlopen('http://169.254.169.254/latest/meta-data/public-ipv4').read().decode('utf-8')
ip = 'http://'+ip+':'+str(portNum)+'/order/'

response = snsClient.subscribe(
    TopicArn=orderTopic,
    Protocol='http',
    Endpoint=ip
)
'''
def iridium():
    print "Getting Iridium"
    time.sleep(1)
    return 1

def magnesite():
    print "Getting Magnesite"
    time.sleep(1)
    return 1

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
    return "Welcome to the monolith"
    
# Effectively, our subscriber service.
@app.route('/order/', methods=['POST'])
def order():
    if request.method == 'POST':
        try: 
            iridiumResult = 0
            magnesiteResult = 0
            # Is this a normal SNS payload? Try to get JSON out of it
            payload = request.get_json(force=True)
            if 'SubscribeURL' in payload:
                print 'Incoming subscription request from SNS...'
                # print payload['SubscribeURL']
                print 'Sending subscription confirmation to SNS...'
                response = requests.get(payload['SubscribeURL'])
                # print response.status_code
                if response.status_code == requests.codes.ok:
                    return "SNS topic subscribed!"
                else:
                    response.raise_for_status()
            elif 'bundle' in payload['Message']:
                print 'Gathering Requested Items'
                iridiumResult = iridium()
                magnesiteResult = magnesite()
                response = fulfill(apiKey, endpoint, iridiumResult, magnesiteResult)
                if response == requests.codes.ok:
                    print 'Bundle fulfilled'
                    return 'Your order has been fulfilled'
                else:
                    # print response
                    return 'Your order has NOT been fulfilled'
	    else: 
		print 'SOMETHING IS WEIRD'
        except Exception as e:
            # Looks like it wasn't.
            print e
            print 'This was not a fulfillment request. Moving on...'
            return 'We were unable to place your order'
        
        return "This was not a fulfillment request. Moving on..."
    else:
        # We should never get here
        return "This is not the page you are looking for"

# Fulfillment service
# Expects a POST of {'thing': '1'} from microservice until we separate fulfillment into its own microservice as well
# def fulfill(apiKey, endpoint, iridium, magnesite)
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
