#!bin/python

import time
from flask import Flask
from flask import request
import json
import requests
import boto3

# Get API Key and parameters from SSM

indexPage = '''

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Admin Page</title>

  </head>

  <body>
    
    <div class="container">
      <form action="/">
        <h2>Admin Page</h2>
        <input type="text" id="Bundle" placeholder="username">
        <button class="btn btn-lg btn-primary btn-block" type="submit">Submit</button>
      </form>
    </div> <!-- /container -->

    <div class="container">
        <form class="form-snsSub">
          <h2 class="form-snsSub-heading">SNS Subscription</h2>
          <label for="inputUrl" class="sr-only">Url</label>
          <input type="text" id="inputUrl" class="form-control" placeholder="Url">
          <ul class="list-group">
              <li id="subMonolith" class="list-group-item">Receive bundled resources</li>
              <li id="subDilithiumCrystals" class="list-group-item">Receive Delithium Crystals</li>
              <li id="subSpaceMelange" class="list-group-item">Receive Space Melange</li>
              <li id="subTiberium" class="list-group-item">Receive Tiberium</li>
              <li id="subVespeneGas" class="list-group-item">Receive Vespene Gas</li>
            </ul>
        </form>
    </div> <!-- /container -->

    <!-- Bootstrap core JavaScript================================================== -->
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js" integrity="sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://sdk.amazonaws.com/js/aws-sdk-2.128.0.min.js"></script>
    <script type="text/javascript" src="https://s3-us-west-2.amazonaws.com/www.interstella.trade/getkey.js"></script>
    <script src="https://use.fontawesome.com/68e1a8f14b.js"></script>
    <!-- Placed at the end of the document so the pages load faster -->
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="https://s3-us-west-2.amazonaws.com/www.interstella.trade/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>
'''

portNum = 5000

application = Flask(__name__)

@application.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return "Welcome to the Admin console"
    if request.method == 'POST':
        return 'Hi'

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=portNum)
