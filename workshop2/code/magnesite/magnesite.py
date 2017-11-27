#!bin/python

import time
from flask import Flask
from flask import request
import json
import requests
import os
import boto3
from urllib2 import urlopen
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# This should be the endpoint of the monolith
endpoint = os.getenv('monolithUrl')
portNum = 80
resource = 'magnesite'
region = urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read().decode('utf-8')

ssmClient = boto3.client('ssm',region_name=region[:-1])
orderTopic = ssmClient.get_parameter(Name='/interstella/magnesite')['Parameter']['Value']
orderTopicRegion = orderTopic.split(':')[3]

# SNS Subscribe
snsClient = boto3.client('sns',region_name=orderTopicRegion)
ip = urlopen('http://169.254.169.254/latest/meta-data/public-ipv4').read().decode('utf-8')
ip = 'http://'+ip+':'+str(portNum)+'/'+resource+'/'

response = snsClient.subscribe(
    TopicArn=str(orderTopic),
    Protocol='http',
    Endpoint=ip
)

def produceResource():
    print "Producing "+resource
    #time.sleep(1)
    return

def fulfill(endpoint, number):
    if endpoint == '':
        return 'Missing endpoint'
    else:
        fullEndpoint = 'http://'+str(endpoint)+':5000/fulfill/'
        data = {resource : number}
        try:
            response = requests.post(fullEndpoint, data=json.dumps(data))
            if response.status_code == requests.codes.ok:
                print response.status_code
                return response.status_code
            else:
                response.raise_for_status()
        except Exception as e:
            response = e
    return response

app = Flask(__name__)
    
# Effectively, our subscriber service.
@app.route('/'+resource+'/', methods=['POST', 'GET'])
def order():
    #This is for health checking
    if request.method == 'GET':
        return 'Welcome to the '+resource+' microservice'
    #Real requests
    elif request.method == 'POST':
        try: 
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
            elif (len(json.loads(payload['Message']))) == 1 and resource in payload['Message']:
                print 'Gathering Requested Items'
                produceResource()
                response = fulfill(endpoint, 1)
                if response == requests.codes.ok:
                    print 'Spice fulfilled'
                    return 'Your order has been fulfilled'
                else:
                    print response
                    return 'Your order has NOT been fulfilled'
            else: 
                print 'Invalid Request JSON.'
                print 'The data sent was %s' % payload['Message']
        except Exception as e:
            # Looks like it wasn't.
            print e
            print 'This was not a fulfillment request. This microservice is expecting exactly {"'+resource+'": 1}'
            print 'The data sent was %s' % payload['Message']
            return 'We were unable to place your order'
            

        return 'This was not a fulfillment request. This microservice is expecting exactly {"'+resource+'": 1}'
        
    else:
        # We should never get here
        return "This is not the page you are looking for"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=portNum)
