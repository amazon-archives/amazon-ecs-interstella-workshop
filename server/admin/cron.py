#!bin/python
import boto3
import sched, time

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

table = dynamodb.Table('requestRates')

snsClient = boto3.client('sns',region_name='us-west-2')

# SNS ARNs for topics.
iridiumArn = 'arn:aws:sns:us-west-2:270206935686:iridium'
orderTopicArn = 'arn:aws:sns:us-west-2:270206935686:orderTopic'
magnesiteArn = 'arn:aws:sns:us-west-2:270206935686:magnesite'

while True:
    response = table.scan()
    print response
    for i in range(0, response['Count']):
        print '========================================='
        print 'Publishing to...'
        print 'Resource: '+ response['Items'][i]['resource']
        print 'Rate: ' + str(response['Items'][i]['rate'])
        if response['Items'][i]['resource'] == 'orderTopic':
            data = '{"bundle": 1}'
            arn = orderTopicArn
        elif response['Items'][i]['resource'] == 'iridium':
            data = '{"iridium": 1}'
            arn = iridiumArn
        elif response['Items'][i]['resource'] == 'magnesite':
            data = '{"magnesite": 1}'
            arn = magnesiteArn
        else:
            data = '{"bundle": 1}'
            arn = orderTopicArn
        for j in xrange(response['Items'][i]['rate']):
            #arn='arn:aws:sns:us-west-2:270206935686:'+response['Items'][i]['resource']
            snsResponse = snsClient.publish(TopicArn=arn, Message=data)
            print snsResponse

    time.sleep(30)
