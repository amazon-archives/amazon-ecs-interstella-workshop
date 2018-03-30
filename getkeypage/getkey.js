AWS.config.update({
    region: 'us-west-2'
});
var ddb, apigateway, sns;

$('.spinner').hide();
$('.keywindow').hide();

function putUserInDDB(userName, apiKey){
    const utcTimeStamp = new Date().toISOString();
    // calculate current UTC time + 30 days in milliseconds and divide 1000 to get epoch time
    const ttl = Math.round((new Date().getTime() + 2592000000) / 1000).toString();

    var params = {
        TableName: 'UsernameAPIKeyMap',
        Item: {
            'username': {
                S: userName
            },
            'apikey': {
                S: apiKey
            },
            'keycreationdate': {
                S: utcTimeStamp
            }, 
            'ttl': {
                S: ttl
            }
        }
    };

    // Call DynamoDB to read the item from the table
    ddb.putItem(params, function(err, data) {
        if (err === null){
            $('.spinner').hide();
            $('.keywindow').show();
            $('#key-display').text(apiKey);
            $('#ttl-display').text("30");
        }            
        if (err)
            alert(err);
    });
}

function createAPIKey(name){
    var params = {
        //customerId: 'STRING_VALUE',
        description: 'test description',
        enabled: true,
        generateDistinctId: true,
        name: name,
        stageKeys: [
          {
            restApiId: 'x5j9vob844',
            stageName: 'production'
          }          
        ]//,
        //value: 'STRING_VALUE'
      };
      
      apigateway.createApiKey(params, function(err, data) {
        if (err === null && data.value){                      
            putUserInDDB(name, data.value);
            associateKeyToPlan(data.id);
        }
        if (err)
            alert(err);
      });
}

function associateKeyToPlan(id){
    var params = {
        keyId: id, /* required */
        keyType: 'API_KEY', /* required */
        usagePlanId: 'm4rgiw' /* required */
      };
      apigateway.createUsagePlanKey(params, function(err, data) {
        if (err) alert(err); // an error occurred
        //else     console.log(data);           // successful response
      });
}

function DisplayKey(){
    
    var userName = $('#login-username').val();
    var params = {
        TableName: 'UsernameAPIKeyMap',
        Key: { 
            'username': {
                S: userName
            }
        }
    };

    AWS.config.credentials.refresh(function(err){
        if (err)
            alert(err);

        ddb.getItem(params, function(err, data) {
            if (err === null && data.Item === undefined){
                $('.spinner').show();
                createAPIKey(userName); 
            }
            if (err === null && data.Item){
                $('.keywindow').show();
                $('#key-display').text(data.Item.apikey.S);
                if (data.Item.ttl.S){
                    const ttl = parseInt(data.Item.ttl.S);
                    const now = (new Date().getTime() / 1000);
                    const exp = Math.round((ttl - now)/86400);
                    $('#ttl-display').text(exp.toString());
                }
                
            }
            if (err !== null && err.indexOf("UserNotFoundException") !== -1){
                alert("User not found. Please sign up first.");
            }
            if (err){
                alert(err);    
            }

        });
    });
}

$(function() {       
    // $(".form-signin").submit(function(event) {
    //     try{
    //         $('.spinner').hide();
    //         $('.keywindow').hide();
    //         DisplayKey();       
    //         event.preventDefault();
    //     } catch (e){
    //         throw e;
    //     }
    // });

    $("#btn-login").click(function(event){
        $('.spinner').hide();
        $('.keywindow').hide();
        var username = $("#login-username").val();
        var password = $("#login-password").val();
        
        var authenticationData = {
            Username : username,
            Password : password,
        };
        var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);
        var poolData = {
            UserPoolId : 'us-west-2_RyRT8F4ly', // Your user pool id here
            ClientId : 'u8h0kgf0aaldbvg4j7c84ipok' // Your client id here
        };
        var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);
        var userData = {
            Username : username,
            Pool : userPool
        };
        var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                
                //alert('access token + ' + result.getAccessToken().getJwtToken());
                AWS.config.credentials = new AWS.CognitoIdentityCredentials({
                    IdentityPoolId : 'us-west-2:766a71c6-eca1-474a-94d2-ae87a94ee697', // your identity pool id here
                    Logins : {
                        // Change the key below according to the specific region your user pool is in.
                        'cognito-idp.us-west-2.amazonaws.com/us-west-2_RyRT8F4ly' : result.getIdToken().getJwtToken()
                    }
                });
                AWS.config.credentials.clearCachedId();
                AWS.config.credentials.get(function(err){
                    if (err) {
                        alert(err);
                    }
                    ddb = new AWS.DynamoDB({apiVersion: '2012-10-08'});
                    apigateway = new AWS.APIGateway({apiVersion: '2015-07-09'});
                    sns = new AWS.SNS({apiVersion: '2010-03-31'});
                    
                    try{
                        DisplayKey();       
                    } catch (e){
                        throw e;
                    }
                });
                
                $('.form-keywindow').show();

                event.preventDefault();
            },
    
            onFailure: function(err) {
                if (err.code === "UserNotFoundException")
                alert("User not found. Please sign up first.");
                $('.form-keywindow').hide();
            }
    
        });

        event.preventDefault();
    });

    $("#btn-signup").click(function(event){
        $('.spinner').hide();
        $('.keywindow').hide();
        var username = $("#signup-username").val();
        var password = $("#signup-password").val();

        var poolData = {
            UserPoolId : 'us-west-2_RyRT8F4ly', // Your user pool id here
            ClientId : 'u8h0kgf0aaldbvg4j7c84ipok' // Your client id here
        };
        var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);

    
        userPool.signUp(username, password, null, null, function(err, result){
            if (err) {
                alert(err);
                return;
            }
            cognitoUser = result.user;
            //alert('user name is ' + cognitoUser.getUsername());
            //alert('Sign up successful. Please sign in now.');
            $('#signupbox').hide();
            $('#loginbox').show();  
            //fill in user name and password
            $("#login-username").val(username);
            $("#login-password").val(password);

            $("#btn-login").trigger("click");
            
        });
        event.preventDefault();
    });

    $("#subOrders").click(function(event){
        if (sns === undefined){
            alert("Please log in first.");
            return;
        }
        var url = $('#inputUrl').val();
        var params = {
            Protocol: 'http', /* required */
            TopicArn: 'arn:aws:sns:us-west-2:270206935686:orderTopic', /* required */
            Endpoint: url
          };
        sns.subscribe(params, function(err, data) {
            if (err) alert(err); // an error occurred
            else alert(data.SubscriptionArn);           // successful response
        });
        event.preventDefault();
    });

    $("#subIridium").click(function(event){
        if (sns === undefined){
            alert("Please log in first.");
            return;
        }
        var url = $('#inputUrl').val();
        var params = {
            Protocol: 'http', /* required */
            TopicArn: 'arn:aws:sns:us-west-2:270206935686:iridium', /* required */
            Endpoint: url
          };
        sns.subscribe(params, function(err, data) {
            if (err) alert(err); // an error occurred
            else alert(data.SubscriptionArn);           // successful response
        });
        event.preventDefault();
    });

    $("#subMagnesite").click(function(event){
        if (sns === undefined){
            alert("Please log in first.");
            return;
        }
        var url = $('#inputUrl').val();
        var params = {
            Protocol: 'http', /* required */
            TopicArn: 'arn:aws:sns:us-west-2:270206935686:magnesite', /* required */
            Endpoint: url
          };
        sns.subscribe(params, function(err, data) {
            if (err) alert(err); // an error occurred
            else alert(data.SubscriptionArn);           // successful response
        });
        event.preventDefault();
    });
});