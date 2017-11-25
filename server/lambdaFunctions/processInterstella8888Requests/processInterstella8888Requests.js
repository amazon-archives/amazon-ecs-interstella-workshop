'use strict';

var AWS = require('aws-sdk');
//var dynamodb = new AWS.DynamoDB({apiVersion: '2012-08-10'});
var documentClient = new AWS.DynamoDB.DocumentClient();
exports.handler = (event, context, callback) => {
    var tableName = "myTableName";
    var datetime = new Date().toISOString();
    console.log(event.body);
    var key = 'not-initiated';
    if (event.headers !== null && event.headers !== undefined) {
        if (event.headers['x-api-key'] !== undefined && event.headers['x-api-key'] !== null && event.headers['x-api-key'] !== "") {
            key = event.headers['x-api-key'];
        }
        else{
            callback(new Error('Error - Header x-api-key not found. Please include your API key with x-api-key header'))
        }
    }
    var params = {
      TableName : 'myTableName',
      Item: {
         api_key: key,
         timestamp: datetime,
         production: JSON.parse(event.body)
      }
    };
    /*dynamodb.putItem({
        "TableName": tableName,
        "Item" : {
            "api_key": {"S": key },
            "timestamp": {"S": datetime },
            "user": {"S": "user" },
            "msg": {"S": "message"},
            "fulfillment": JSON.parse(event.body)
        }*/
    documentClient.put(params, function(err, data) {
        if (err) {
            // console.log(err, err.stack)
            callback(new Error('internal server error: ' + err.stack))
        }
        else {
            // console.log('success: ' + JSON.stringify(data, null, '  '));
            callback(null, {"statusCode": 200, "body": "success"})
        }
    });
};