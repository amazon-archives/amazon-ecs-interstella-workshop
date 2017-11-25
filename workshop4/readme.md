# Interstella 8888: Advanced Microservice Operations

## Overview:
Welcome to the Interstella 8888 team!  Interstella 8888 is an intergalactic trading company that deals in rare resources.  This is the last workshop in a series of Amazon EC2 Container Service (ECS) workshops where Interstella 8888 modernized its legacy monolithic infrastructure and made it more reliable, scalable and secure by moving towards a microservices architecture.  In this last workshop, Interstella 8888 has nearly completed infrastructure transformation and is ready to harden its insfrastructure for production.  

This workshop will walk you through load testing with [Gatling](https://gatling.io/), debugging with [AWS X-Ray](https://aws.amazon.com/xray/), and increasing service to service communication resiliency with [linkerd](https://linkerd.io/). 

At this point, Interstella's applications have been containerized and decoupled into microservices.  Before deploying to production, Interstella 8888 wants to learn how its new application architecture behaves under stress. They would also like to learn how to trace errors easily in this highly distributed environment. With previous monolithic architecture, it was easier to find errors because all application layers were hosted on the same machine. In a distributed environment, requests paths are more complicated and it can be difficult to identify root cause. Lastly, as Interstella 8888 expands on this microservice pattern, communication between services becomes another concern in a distributed environment. We will be learning how a service mesh can add service discovery, load balancing, failure handling, instrumentation, and routing to all inter-service communication

### Requirements:  
* AWS account - if you don't have one, it's easy and free to [create one](https://aws.amazon.com/)
* AWS IAM account with elevated privileges allowing you to interact with CloudFormation, IAM, EC2, ECS, ECR, ELB/ALB, VPC, SNS, CloudWatch
* A workstation or laptop with an ssh client installed, such as [putty](http://www.putty.org/) on Windows; or terminal or iterm on Mac
* Familiarity with Python, vim/emacs/nano, [Docker](https://www.docker.com/), and AWS - not required but a bonus

### Labs:  
These labs are designed to be completed in sequence, and the full set of instructions are documented below.  Read and follow along to complete the labs.  If you're at a live AWS event, the workshop attendants will give you a high level run down of the labs and be around to answer any questions.  Don't worry if you get stuck, we provide hints along the way.  

* **Workshop Setup:** Setup working environment on AWS  
* **Lab 1:** Build and deploy ECS services
* **Lab 2:** Load test with Gatling
* **Lab 3:** Debugging distributed applications with AWS X-Ray
* **Lab 4:** Increase inter-service communication resiliency with linkerd

### Conventions:  
Throughout this workshop, we provide commands for you to run in the terminal.  These commands will look like this: 

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_DNS_NAME</i></b>
</pre>

The command starts after the $.  Text that is ***UPPER_ITALIC_BOLD*** indicates a value that is unique to your environment.  For example, the ***PRIVATE\_KEY.PEM*** refers to the private key of an SSH key pair that you've created, and the ***EC2\_PUBLIC\_DNS\_NAME*** is a value that is specific to an EC2 instance launched in your account.  You can find these unique values either in the CloudFormation outputs or by going to the specific service dashboard in the AWS management console. 

### Workshop Cleanup:
You will be deploying infrastructure on AWS which will have an associated cost.  Fortunately, this workshop should take no more than 2 hours to complete, so costs will be minimal.  When you're done with the workshop, follow these steps to make sure everything is cleaned up.  

1. Delete any manually created resources throughout the labs.  Certain things do not have a cost associated, and if you're not sure what has a cost, you can always look it up on our website.  All of our pricing is publicly available, or feel free to ask one of the workshop attendants when you're done. 
2. Delete any container images stored in ECR, delete CloudWatch logs groups, and delete ALBs and target groups (if you get to that lab) 
3. Delete the CloudFormation stack launched at the beginning of the workshop to clean up the rest.

* * * 

## Let's Begin!  
  
### Workshop Setup:

1\. Log into the AWS Management Console and select an [AWS region](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html).  The region dropdown is in the upper right hand corner of the console to the left of the Support dropdown menu.  For this lab, choose either **Ohio** or **Oregon**. 

2\. Create an [SSH key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) that will be used to login to launched EC2 instances.  If you already have an SSH key pair and have the PEM file (or PPK in the case of Windows Putty users), you can skip to the next step.  

Go to the EC2 Dashboard and click on **Key Pairs** in the left menu under Network & Security.  Click **Create Key Pair**, provide a name (e.g. interstella-workshop), and click **Create**.  Download the created .pem file, which is your private SSH key.      

*Mac or Linux Users*:  Change the permissions of the .pem file to be less open using this command:  

<pre>$ chmod 400 <b><i>PRIVATE_KEY.PEM</i></b></pre>  
  
*Windows Users*: Convert the .pem file to .ppk format to use with Putty.  Here is a link to instructions for the file conversion - [Connecting to Your Linux Instance from Windows Using PuTTY](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)  
  
3\. Generate a Fulfillment API Key for the logistics software [here](http://www.interstella.trade/getkey.html).  Create a username and password to login to the API Key Management portal; you'll need to access this page again later in the workshop, so don't forget what they are.  Click **GetKey** to generate an API Key.  Note down your username and API Key because we'll be tracking resource fulfillment rates.  The API key will be used later to authorize the logistics software send messages to the order fulfillment API endpoint (see arch diagram in Lab 1).  

4\. For your convenience, we provide a [CloudFormation](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) template to stand up core workshop infrastructure.  

Here is what the workshop environment looks like:  

![CloudFormation Starting Stack](images/starthere.png)  

The CloudFormation template will launch the following:
* VPC with public subnets, routes and Internet Gateway
* EC2 Instances with security groups (inbound tcp 22, 80, 5000) and joined to an ECS cluster 
* ECR repositories for your container image
* Parameter store to hold values for API Key, fulfillment API endpoint, and SNS Orders topic

*Note: SNS Orders topic, S3 assets, API Gateway and DynamoDB tables are admin components that run in the workshop administrator's account.  If you're at a live AWS event, this will be provided by the workshop facilitators.  We're working on packaging up the admin components in an admin CloudFormation template, so you can run this workshop at your office, home, etc.*

Click on the CloudFormation launch template link below for the region you selected in Step 1.  The link will load the CloudFormation Dashboard and start the stack creation process in the specified region.

Region | Launch Template
------------ | -------------  
**Ohio** (us-east-2) | [Launch Interstella CloudFormation Stack in Ohio](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=Interstella-workshop&templateURL=https://s3-us-west-2.amazonaws.com/www.interstella.trade/workshop4/starthere.yaml)  
**Oregon** (us-west-2) | [Launch Interstella CloudFormation Stack in Oregon](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=Interstella-workshop&templateURL=https://s3-us-west-2.amazonaws.com/www.interstella.trade/workshop4/starthere.yaml) 

You should be on the Select Template page, notice an S3 URL link to the CloudFormation template is already populated.  Click **Next** to continue without modifying any fields on this page.    

5\. On the Specify Details step of the Create Stack process, enter values for the following fields:
* **EnvironmentName** - this name is to used to tag resources created by CloudFormation
* **KeyPairName** - select the key pair that you created from Step 1
* **InterstellaApiKey** - enter the API key generated from Step 3
* **InterstellaApiEndpoint** - enter the fulfillment API endpoint provided by workshop admins
* **InterstellaOrdersTopicArn** - enter the SNS Orders topic provided by workshop admins

All other fields can be left as their default values.  

Click **Next** to move on to the Options page.  

6\. No changes or inputs are required on the Options page.  Click **Next** to move on to the Review page.

7\. On the Review page, scroll down to the Capabilities section and click on the checkbox next to *"I acknowledge that AWS CloudFormation might create IAM resources with custom names."*.  If you do not check this box, the stack creation will fail.

![CloudFormation acknowledgement](images/0-cloudformation-create.png)

Click **Create** to launch the CloudFormation stack. 

### Checkpoint:  
The CloudFormation stack will take a few minutes to lauch.  Periodically check on the stack creation process in the CloudFormation Dashboard.  Your stack should show status **CREATE\_COMPLETE** in roughly 5-10 minutes.  If you select box next to your stack and click on the **Events** tab, you can see what steps it's on.  

If there was an [error](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html#troubleshooting-errors) during the stack creation process, CloudFormation will rollback and terminate.  You can investigate and troubleshoot by looking in the Events tab.  Any errors encountered during stack creation will appear in the event stream as a failure.

* * * 

### Lab 1 - Build and deploy monolith container using Amazon ECS:    

**NOTE**: If you are coming from previous workshops in this series, you will already have done this part and you may skip to lab 2. However, in the case that this is the first workshop you are attending in this series or you have deleted resources created in last workshop, you will need to run through this Lab. 

In this lab, you will build the logistics software (i.e. monolith) Docker image from a provided Dockerfile and deploy the container using ECS.  If you're new to ECS or need a refresher, ECS is a container management service for deploying Docker containers across a fleet of EC2 instances.  ECS uses a JSON formatted template called a [Task Definition](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html) that describes one or more containers that make up your application or unit of work.  With task definitions, you can specify things like container image(s) you want to use, host:container port mappings, cpu and memory allocations, logging, and more.   

Here is a reference architecture for what you will be implementing in Lab 1:

![Lab 1 Architecture](images/workshop2-lab1.png)

*Reminder: You'll see SNS topics, S3 bucket, API Gateway and DynamoDB in the diagram.  These are provided by Interstella HQ for communicating orders and fulfilling orders.  They're in the diagram to show you the big picture as to how orders come in to the logistics platform and how orders get fulfilled*

*If you are attending a live AWS event, these assets will be provided.  We're working on packaging up the admin components, so you can run this workshop at your office, home, etc.*

1\. SSH into one of the launched EC2 instances to get started.  

Go to the EC2 Dashboard in the Management Console and click on **Instances** in the left menu.  Select either one of the EC2 instances created by the CloudFormation stack and SSH into the instance.  

*Tip: If your instances list is cluttered with other instances, type the **EnvironmentName** you used when running your CloudFormation template into the filter search bar to reveal only those instances.*  

![EC2 Public IP](images/1-ec2-IP.png)

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_IP_ADDRESS</i></b>
</pre>

If you see something similar to the following message (host IP address and fingerprint will be different, this is just an example) when trying to initiate an SSH connection, this is normal when trying to SSH to a server for the first time.  The SSH client just does not recognize the host and is asking for confirmation.  Just type **yes** and hit **enter** to continue:

<pre>
The authenticity of host '52.15.243.19 (52.15.243.19)' can't be established.
RSA key fingerprint is 02:f9:74:ef:d8:5c:19:b3:27:37:57:4f:da:37:2b:e8.
Are you sure you want to continue connecting (yes/no)? 
</pre>

2\. Once logged onto the instance, download the logistics application source, requirements file, and a draft Dockerfile from Interstella's S3 static site.  

Note: the flag for the curl command below is a capital O, not a zero.   

<pre>
$ curl -O http://www.interstella.trade/workshop2/code/monolith/monolith.py
$ curl -O http://www.interstella.trade/workshop2/code/monolith/requirements.txt
$ curl -O http://www.interstella.trade/workshop2/code/monolith/Dockerfile
</pre>

3\. Build the image using the [Docker build](https://docs.docker.com/engine/reference/commandline/build/) command.  This command needs to be run in the same directory where your Dockerfile is and note the trailing period which tells the build command to look in the current directory for the Dockerfile.

<pre>
$ docker build -t monolith .
</pre> 

You'll see a bunch of output as Docker builds all the layers to the image.  If there is a problem along the way, the build process will fail and stop.  Otherwise, you'll see a success message at the end of the build output like this:

<pre>
Step 15/15 : ENTRYPOINT bin/python monolith.py
---> Running in 188e00e5c1af
---> 7f51e5d00cee
Removing intermediate container 188e00e5c1af
Successfully built 7f51e5d00cee
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

You can list your docker images to see the image you just built.  Here's a sample output, note the monolith image in the list: 

<pre>
[ec2-user@ip-10-177-10-249 ~]$ docker images
REPOSITORY               TAG        IMAGE ID        CREATED             SIZE
monolith                 latest     87d3de20e191    17 seconds ago      532 MB
&lt;none&gt;                   &lt;none&gt;     850d78c7aa5f    27 minutes ago      735 MB
golang                   1.9        1a34fad76b34    8 days ago          733 MB
ubuntu                   14.04      3aa18c7568fc    8 days ago          188 MB
amazon/amazon-ecs-agent  latest     96e5393c89d4    6 weeks ago         25.4 MB
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

4\. Run the docker container to make sure it is working as expected.  Interstella's logistics platform will automatically subscribe to the SNS orders feed and is configured to send fulfillment to the order fulfillment API.  When you issue the [docker run](https://docs.docker.com/engine/reference/run/) command, the -p flag is used to map the host listening port to the container listening port.  

<pre>
$ docker run -p 5000:5000 monolith
</pre>

Here's a sample output:

<pre>
[ec2-user@ip-10-177-10-249 ~]$ docker run -p 5000:5000 monolith
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 265-056-304
54.240.230.188 - - [13/Nov/2017 01:46:52] "POST /order/ HTTP/1.1" 200 -
54.240.230.246 - - [13/Nov/2017 01:46:53] "POST /order/ HTTP/1.1" 200 -
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

Use **Ctrl-C** to stop the container.  

5\. Now that you have a deployable container, tag and push the image to ECR.  Not only does this allow for version control and persistence, but ECS will reference the image from ECR when deploying the container.    

In the AWS Management Console, navigate to the EC2 Container Service dashboard and click on **Repositories** in the left menu.  You should see the repository created by CloudFormation named the EnvironmentName (in the example below, I used 'bamazon' as my EnvironmentName) specified during stack creation.  

![ECR repositories](images/1-ecr-repo.png)

Click on the repository name, and note the Repository URI:

![ECR monolith repo](images/1-ecr-repo-uri.png)

*Note: Your repository URI will be unique.*

Tag and push your container image to the repository.

<pre>
$ docker tag monolith:latest <b><i>ECR_REPOSITORY_URI</i></b>:latest
$ docker push <b><i>ECR_REPOSITORY_URI</i></b>:latest
</pre>

When you issue the push command, Docker pushes the layers up to ECR, and if you refresh the monolith repository page, you'll see an image indicating the latest version.  

*Note: that you did not need to authenticate docker with ECR because the [Amazon ECR Credential Helper](https://github.com/awslabs/amazon-ecr-credential-helper) has been installed and configured for you on the EC2 instance.  This was done as a bootstrap action when launching the EC2 instances.  Review the CloudFormation template and you will see where this is done.  You can read more about the credentials helper in this blog article - https://aws.amazon.com/blogs/compute/authenticating-amazon-ecr-repositories-for-docker-cli-with-credential-helper/*

![ECR push complete](images/1-ecr-push-complete.png)

***====> TODO: CONTINUE HERE***

*Note: You will use the AWS Management Console for this lab, but remember that you can programmatically accomplish the same thing using the AWS CLI or SDKs or CloudFormation.*

1\. In the AWS Management Console, navigate to the EC2 Container Service dashboard.  Click on **Task Definitions** in the left menu.  Click on **Create New Task Definition**.  

2\. Enter a name for your Task Definition, e.g. interstella-monolith.  Leave Task Role and Network Mode as defaults. 

*Tip: The next step will reference the container image you pushed to ECR, so make sure you have the ECR repository URI for the monolith container handy.*

3\. Click **Add container**.  Enter values for the following fields:
* **Container name** - this is a logical identifier, not the name of the container image, e.g. monolith
* **Image** - this is a reference to the container image stored in ECR.  The format should be the same value you used to push the container to ECR - <pre><b><i>ECR_REPOSITORY_URI</i></b>:latest</pre>
* **Memory Limits** - select **Soft limit** from the drop down, and enter **128**.  

*Note: This assigns a soft limit of 128MB of RAM to the container, but since it's a soft limit, it does have the ability to consume more available memory if needed.  A hard limit will kill the container if it exceeds the memory limit.  You can define both for flexible memory allocations.  Resource availability is one of the factors that influences container placement.  You can read more about [ContainerDefinitions](http://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html) in our documentation*

* **Port mappings** - enter **5000** for both the host and container port.  

*Note: You might be wondering how you can more than one of the same container on a single host since there could be conflicts based on the port mappings configuration.  ECS offers a dynamic port mapping feature when using the ALB as a load balancer for your container service.  We'll visit this in the bonus lab when scaling the microservices with ALB*

Leave the remaining fields as is and click **Add** to associate this container with the task definition. 

Here's an example of what the container definition should look like:

![Add container example](images/2-task-def-add-container.png) 

*Note: Your container image URI will be unique.* 

4\. Click **Create** to finish creating the task definition. 

5\. You should be at the task definition view where you can do things like create a new revision or invoke certain actions.  In the **Actions** dropdown, select **Run Task** to launch your container.  

![Run Task](images/2-run-task.png)

6\. Leave all the fields as their defaults and click **Run Task**. 

*Note: There are many options to explore in the Task Placement section of the Run Task action, and while we will not touch on every configuration in this workshop, you can read more about [Scheduling Tasks](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduling_tasks.html) in our documentation.*

You'll see the task start in the **PENDING** state.  

![Task state](images/2-task-state-pending.png)

In a few seconds, click on the refresh button until the task changes to a **RUNNING** state. 

![Task state](images/2-task-state-running.png)

7\. In the previous lab, you attached to the running container to get stdout.  While you could do still do that, there's a better way to handle logging.  ECS offers integration with CloudWatch logs through an awslogs driver that can be enabled in the container definition. 

First, stop the task that you ran in the last step.  You can do this by selecting the checkbox next to the running task and clicking the **Stop** button.

Next, create a log destination called a CloudWatch log group.  Navigate to the CloudWatch dashboard and click on **Logs** in the left menu.  In the **Actions** drop down, select **Create log group** and enter a name for the group, e.g. interstella-monolith  

![CloudWatch Log Group](images/2-cloudwatch-logs.png)  

8\. Next update the monolith container definition in the task definition you created to enable the logs driver.  

Navigate to the EC2 Container Service dashboard and click **Task Definitions** in the left menu.  Select the task definition you created earlier and click **Create new revision**.

![Task Def New Revision](images/2-task-def-new-rev.png) 

Under **Container Definitions**, click on the monolith container definition you created earlier.  You'll see the Standard options that you had set.  Scroll down to **Storage and Logging** options and find the **Log configuration** section.  Select **awslogs** from the *Log driver* dropdown. For *Log options*, enter the name of the CloudWatch log group that you created in step 7 and enter the AWS region of the log group.

![CloudWatch Logs integration](images/2-awslogs-config.png)

Click **Update** to finalize the updates to the container definition, and click **Create** to create the new revision of your task definition.  Notice your task definition's revision number incremented. 

9\. Let's test the new revision of the task definition.  In the **Actions** drop down menu, select **Run Task**.  Leave the defaults and click **Run Task**.  If you get stuck, refer back to steps 5-6.  

Once your task is running, navigate back to the CloudWatch Logs dashboard, and click on your log group.  As your container processes orders, you'll see a log stream appear in the log group reflecting the HTTP POST logs written to stdout you saw earlier.  

![CloudWatch Log Stream](images/2-cwl-confirm.png)

Click on the log stream to view log entries.    

![CloudWatch Log Entries](images/2-cwl-logs.png)

### Checkpoint:  
At this point you have a working container for the monolith codebase stored in an ECR repository.  You've created a task definition and are able to repeatedly deploy the monolith container using ECS.  You've also enabled logging to CloudWatch Logs, so you can verify your container is working as expected.  Now you're ready to tackle a bigger challenge, horizontally scaling the containerized logistics platform, so you can process more orders and as a bonus improve the fault tolerance.  Let's get to it! 

* * *

### Lab 2 - Load Test with Gatling:   

In this lab, you will build a Gatling container and use it perform load tests on Interstella infrastructure. Gatling is an open-source load testing framework based on Scala, Akka and Netty. The software is designed to be used as a load testing tool for analyzing and measuring the performance of a variety of services, with a focus on web applications. Gatling can simulate large number of users with complex behaviors, collect and aggregate requests response times, and create reports and analytics data. Encapsulating Gatling in containers creates a portable load generator that can easily be scaled up when demand is high and scaled down or taken offline when demand is low.

Here is a reference architecture for what you will be implementing in Lab 2:

![Lab 2 Architecture](images/workshop1-lab2.png)

*Note: You will use the AWS Management Console for this lab, but remember that you can programmatically accomplish the same thing using the AWS CLI or SDKs or CloudFormation.*

1\. SSH into one of the launched EC2 instances to get started.  

Go to the EC2 Dashboard in the Management Console and click on **Instances** in the left menu.  Select either one of the EC2 instances created by the CloudFormation stack and SSH into the instance.  

*Tip: If your instances list is cluttered with other instances, type the **EnvironmentName** you used when running your CloudFormation template into the filter search bar to reveal only those instances.*  

![EC2 Public IP](images/1-ec2-IP.png)

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_IP_ADDRESS</i></b>
</pre>

If you see something similar to the following message (host IP address and fingerprint will be different, this is just an example) when trying to initiate an SSH connection, this is normal when trying to SSH to a server for the first time.  The SSH client just does not recognize the host and is asking for confirmation.  Just type **yes** and hit **enter** to continue:

<pre>
The authenticity of host '52.15.243.19 (52.15.243.19)' can't be established.
RSA key fingerprint is 02:f9:74:ef:d8:5c:19:b3:27:37:57:4f:da:37:2b:e8.
Are you sure you want to continue connecting (yes/no)? 
</pre>

2\. Once logged onto the instance, download the logistics application source, requirements file, and a draft Dockerfile from Interstella's S3 static site.  

Note: the flag for the curl command below is a capital O, not a zero.   

<pre>
$ curl -O http://www.interstella.trade/workshop4/code/gatling/Dockerfile
$ curl -O http://www.interstella.trade/workshop4/code/gatling/gatling.conf
$ curl -O http://www.interstella.trade/workshop4/code/gatling/InterstellaSim.scala
$ curl -O http://www.interstella.trade/workshop4/code/gatling/run.sh
</pre>

3\. Build the image using the [Docker build](https://docs.docker.com/engine/reference/commandline/build/) command.  This command needs to be run in the same directory where your Dockerfile is and note the trailing period which tells the build command to look in the current directory for the Dockerfile.

<pre>
$ docker build -t gatling .
</pre> 

You'll see a bunch of output as Docker builds all the layers to the image.  If there is a problem along the way, the build process will fail and stop.  Otherwise, you'll see a success message at the end of the build output like this:

<pre>
Step 15/15 : ENTRYPOINT bin/python monolith.py
---> Running in 188e00e5c1af
---> 7f51e5d00cee
Removing intermediate container 188e00e5c1af
Successfully built 7f51e5d00cee
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

You can list your docker images to see the image you just built.  Here's a sample output, note the monolith image in the list: 

<pre>
[ec2-user@ip-10-177-10-249 ~]$ docker images
REPOSITORY               TAG        IMAGE ID        CREATED             SIZE
monolith                 latest     87d3de20e191    17 seconds ago      532 MB
&lt;none&gt;                   &lt;none&gt;     850d78c7aa5f    27 minutes ago      735 MB
golang                   1.9        1a34fad76b34    8 days ago          733 MB
ubuntu                   14.04      3aa18c7568fc    8 days ago          188 MB
amazon/amazon-ecs-agent  latest     96e5393c89d4    6 weeks ago         25.4 MB
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

4\. Run the docker container to make sure it is working as expected.  Interstella's logistics platform will automatically subscribe to the SNS orders feed and is configured to send fulfillment to the order fulfillment API.  When you issue the [docker run](https://docs.docker.com/engine/reference/run/) command, the -p flag is used to map the host listening port to the container listening port.  

<pre>
$ docker run -p 5000:5000 monolith
</pre>

Here's a sample output:

<pre>
[ec2-user@ip-10-177-10-249 ~]$ docker run -p 5000:5000 monolith
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 265-056-304
54.240.230.188 - - [13/Nov/2017 01:46:52] "POST /order/ HTTP/1.1" 200 -
54.240.230.246 - - [13/Nov/2017 01:46:53] "POST /order/ HTTP/1.1" 200 -
</pre>

*Note: Your output will not be exactly like this, but it will be similar.*

Use **Ctrl-C** to stop the container.  

1\. In the AWS Management Console, navigate to the EC2 Container Service dashboard.  Click on **Task Definitions** in the left menu.  Click on **Create New Task Definition**.  

2\. Enter a name for your Task Definition, e.g. interstella-monolith.  Leave Task Role and Network Mode as defaults. 

*Tip: The next step will reference the container image you pushed to ECR, so make sure you have the ECR repository URI for the monolith container handy.*

3\. Click **Add container**.  Enter values for the following fields:
* **Container name** - this is a logical identifier, not the name of the container image, e.g. monolith
* **Image** - this is a reference to the container image stored in ECR.  The format should be the same value you used to push the container to ECR - <pre><b><i>ECR_REPOSITORY_URI</i></b>:latest</pre>
* **Memory Limits** - select **Soft limit** from the drop down, and enter **128**.  

*Note: This assigns a soft limit of 128MB of RAM to the container, but since it's a soft limit, it does have the ability to consume more available memory if needed.  A hard limit will kill the container if it exceeds the memory limit.  You can define both for flexible memory allocations.  Resource availability is one of the factors that influences container placement.  You can read more about [ContainerDefinitions](http://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html) in our documentation*

* **Port mappings** - enter **5000** for both the host and container port.  

*Note: You might be wondering how you can more than one of the same container on a single host since there could be conflicts based on the port mappings configuration.  ECS offers a dynamic port mapping feature when using the ALB as a load balancer for your container service.  We'll visit this in the bonus lab when scaling the microservices with ALB*

Leave the remaining fields as is and click **Add** to associate this container with the task definition. 

Here's an example of what the container definition should look like:

![Add container example](images/2-task-def-add-container.png) 

*Note: Your container image URI will be unique.* 

4\. Click **Create** to finish creating the task definition. 

5\. You should be at the task definition view where you can do things like create a new revision or invoke certain actions.  In the **Actions** dropdown, select **Run Task** to launch your container.  

![Run Task](images/2-run-task.png)

6\. Leave all the fields as their defaults and click **Run Task**. 

*Note: There are many options to explore in the Task Placement section of the Run Task action, and while we will not touch on every configuration in this workshop, you can read more about [Scheduling Tasks](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduling_tasks.html) in our documentation.*

You'll see the task start in the **PENDING** state.  

![Task state](images/2-task-state-pending.png)

In a few seconds, click on the refresh button until the task changes to a **RUNNING** state. 

![Task state](images/2-task-state-running.png)

7\. In the previous lab, you attached to the running container to get stdout.  While you could do still do that, there's a better way to handle logging.  ECS offers integration with CloudWatch logs through an awslogs driver that can be enabled in the container definition. 

First, stop the task that you ran in the last step.  You can do this by selecting the checkbox next to the running task and clicking the **Stop** button.

Next, create a log destination called a CloudWatch log group.  Navigate to the CloudWatch dashboard and click on **Logs** in the left menu.  In the **Actions** drop down, select **Create log group** and enter a name for the group, e.g. interstella-monolith  

![CloudWatch Log Group](images/2-cloudwatch-logs.png)  

8\. Next update the monolith container definition in the task definition you created to enable the logs driver.  

Navigate to the EC2 Container Service dashboard and click **Task Definitions** in the left menu.  Select the task definition you created earlier and click **Create new revision**.

![Task Def New Revision](images/2-task-def-new-rev.png) 

Under **Container Definitions**, click on the monolith container definition you created earlier.  You'll see the Standard options that you had set.  Scroll down to **Storage and Logging** options and find the **Log configuration** section.  Select **awslogs** from the *Log driver* dropdown. For *Log options*, enter the name of the CloudWatch log group that you created in step 7 and enter the AWS region of the log group.

![CloudWatch Logs integration](images/2-awslogs-config.png)

Click **Update** to finalize the updates to the container definition, and click **Create** to create the new revision of your task definition.  Notice your task definition's revision number incremented. 

9\. Let's test the new revision of the task definition.  In the **Actions** drop down menu, select **Run Task**.  Leave the defaults and click **Run Task**.  If you get stuck, refer back to steps 5-6.  

Once your task is running, navigate back to the CloudWatch Logs dashboard, and click on your log group.  As your container processes orders, you'll see a log stream appear in the log group reflecting the HTTP POST logs written to stdout you saw earlier.  

![CloudWatch Log Stream](images/2-cwl-confirm.png)

Click on the log stream to view log entries.    

![CloudWatch Log Entries](images/2-cwl-logs.png)

### Checkpoint:  
You've created a task definition and are able to repeatedly deploy the monolith container using ECS.  You've also enabled logging to CloudWatch Logs, so you can verify your container is working as expected.  Now you're ready to tackle a bigger challenge, horizontally scaling the containerized logistics platform, so you can process more orders and as a bonus improve the fault tolerance.  Let's get to it! 

* * *

### Bonus Lab - Scale the logistics platform with ALB: 

By now you have successfully deployed Interstella's logistics software as a container.  If you ran multiple copies of the container/task, there would be more capacity, but each container currently self-registers to the SNS topic.  As a result, the same order would be processed by all running containers.  We need a load balancer to distribute the orders to a pool of containers, so orders are only processed once.  

In this lab, you will update the code to not self-register to the SNS topic.  Then you will implement an ALB to front end your containers.  ALB has a feature called dynamic port mapping for ECS containers, which allows you to run multiple copies of the same container on the same host.  The current task definition maps host port 5000 to container port 5000.  This means you would only be able to run one instance of that task on a specific host.  If the host port configuration in the task definition is set to 0, an ephemeral listening port is automatically assigned to the host and mapped to the container which still listens on 5000.  If you then tried to run two of those tasks, there wouldn't be a port conflict on the host because each task runs on it's own ephemeral port.  These hosts are grouped in a target group for the ALB to route traffic to.    

What ties this all together is an ECS Service, which maintains a desired task count (i.e. n number of containers) and integrates the ALB.  You could take it even further by implementing task auto scaling, but let's set up the foundation first.  And finally, you will register the ALB endpoint with the SNS topic to start the order flow.    

Here is a reference architecture for what you will be implementing in the Bonus Lab:

![Bonus Lab Architecture](images/workshop1-bonus-lab.png)

1\. Disable the logistics platform from self-registering to SNS.  

SSH into the EC2 instance you used to build the container in lab 1 and open monolith.py with your favorite text editor.  Comment out the lines in the app code that subscribes to SNS.  If you're not familiar with Python, you can comment out multiple lines by surrounding the text in triple single quotes, see below:

<pre>
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
</pre> 

Rebuild the container after making these modifications and tag/push a new version of the container image to ECR.  If you do not remember the commands, refer to Lab 1 Step 4 for building the image and Lab 1 Step 6 for tagging and pushing the image up to ECR.  

Notice a few things:
1. When you rebuilt the container, Docker was smart enough to determine that the only change made was in the monolith.py code, so it went straight to that step in the build process.
2. When you pushed the image to ECR, only the changed layers were shipped.  Here's a sample output from the push command: 

<pre>
[ec2-user@ip-10-177-11-69 ~]$ docker push 873896820536.dkr.ecr.us-east-2.amazonaws.com/bamazon:latest
The push refers to a repository [873896820536.dkr.ecr.us-east-2.amazonaws.com/bamazon]
8bec6ba1c46f: Pushed 
0765e0a795f6: Pushed 
98ffa3045297: Pushed 
bab4a9bb3484: Layer already exists 
721e1c8fef33: Layer already exists 
e2c31bad1b89: Layer already exists 
c78ed4c0d7eb: Layer already exists 
3c7ff287f69e: Layer already exists 
f45d7ddce677: Layer already exists 
06a41993c188: Layer already exists 
b9da92eb5509: Layer already exists 
0e08b8ceddd1: Layer already exists 
216eddd97acc: Layer already exists 
c47d9b229ca4: Layer already exists 
latest: digest: sha256:7d723a7ac3173fd1b40c7c985d64b560dc63bc3b6613dd161073748497e2a9b6 size: 3252
</pre>

3. If you look in the ECR repository (go to EC2 Container Service dashboard, click **Respositories** on the left menu), you'll notice in the **Images** tab that a new image has been added.  

![ECR images](images/bonus-ecr-images.png) 

2\. Create an Application Load Balancer.  

In the AWS Management Console, navigate to the EC2 dashboard.  Click on **Load Balancers** in the left menu under the **Load Balancing** section.  Click on **Create Load Balancer**.  Click on **Create** for an Application Load Balancer.  

Give your ALB a name, e.g. interstella.

Under **Listeners**, update the load balancer port to be port **5000**.  

Under **Availability Zones**, select the workshop VPC from the drop-down menu.  You can identify the workshop VPC in the list by the tag, which should be the same as the EnvironmentName from the CloudFormation parameters you provided.  Select one of the Availability Zones (AZ) and select the Public subnet; the **Name** column will indicate which subnet is public.  Repeat with the other AZ.

Leave all other settings as the defaults and click **Next: Configure Security Settings** to move to ALB config Step 2.  The settings should look similar to this:  

![Configure ALB](images/bonus-alb.png)

Since we're not setting up https, click **Next: Configure Security Groups** to move to ALB Step 3.

*Note: It's highly recommend in real world cases to implement SSL encryption for any production systems handling private information.  Our lab is designed to illustrate conceptual ideas and does not implement SSL for simplicity...and it's not a real company.*

You'll notice a security group that starts with your **EnvironmentName** from CloudFormation stack creation and **LoadBalancerSecurityGroup** in the name.  This was provisioned by the CloudFormation template for your convenience.  Select that security group and click **Next: Configure Routing** to move to ALB Step 4.

![Configure ALB Security Group](images/bonus-alb-sg.png)

ALB routes incoming traffic to a target group associated with your ALB listener; targets in this case are the instances hosting your containers.  

Enter a name for the new target group, e.g. monolith.  Enter **5000** for the port.  Leave other settings as defaults and click **Next: Register Targets** to move to ALB Step 5.

![Configure ALB target group](images/bonus-alb-target-group.png)

Amazon ECS handles registration of targets to your target groups, so do you **NOT** have to register targets in this step.  Click **Next: Review**, and on the next page, click **Create**. 

3\. In order to take advantage of dynamic port mapping, create a new revision of your monolith task definition and remove the host port mapping in the container definition.  By leaving the host port blank, an ephemeral port will be assigned and ECS/ALB integration will handle the mapping.  Here's what the new task definition should look like:

![Update Task Definition host port](images/bonus-task-def-host-port.png)

If you need a reminder how to create a new revision of a task definition, review Lab 2 Step 8.

4\. Next create an ECS Service to maintain a desired number of running tasks and tie in the ALB endpoint. 

You should still be on the screen showing the new revision of the task definition you just modified.  Under the **Actions** drop down, choose **Create Service**.

![Configure ECS Service](images/bonus-ecs-service.png)

Enter a name for the service, e.g. monolith, and set **Number of tasks** to be **1** for now.  Keep other settings as their defaults and click **Next Step**

![Create ECS service](images/bonus-ecs-service-1.png)

*Note: Your task definition and cluster name may be unique depending on what you chose for names.*

On the next page, select **Application Load Balancer** for **Load balancer type**.  

You'll see a **Load balancer name** drop-down menu appear.  Select the ALB you created in Step 2.  

In the **Container to load balance** section, select the **Container name : port** combo from the drop-down menu that corresponds to the task definition you edited in step 3.  

![ECS Load Balancing](images/bonus-ecs-service-elb.png) 

Click **Add to load balancer**.  More fields related to the container will appear.  

For the **Listener Port**, select the ALB listener configured earlier.  

For the **Target Group Name**, select the target group created earlier during ALB setup.

Leave the other fields as defaults and click **Next Step**.

![Create ECS Network Container Conf](images/bonus-ecs-service-container.png)

Skip the Auto Scaling configuration by clicking **Next Step**.  

*Note: ECS supports Task auto scaling which can automatically increased and describe your desired task count based on dynamic metrics.  We'll skip this, but this is a very useful feature for production workloads.*  

Click **Create Service**.

*Note: There were many other configuration options, and you can read more about [ECS Services](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html) and [ALB Listeners](http://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html) in our documentation*

Once the Service is created, click **View Service** and you'll see your task definition has been deployed. 

![ECS Service Confirmation](images/bonus-ecs-service-confirm.png)

5\. Subscribe the ALB endpoint to the SNS order topic using the API Key Management Portal (from Workshop Setup Step 3) to start receiving orders.  

To get the ALB endpoint, navigate to the EC2 Dashboard, click on **Load Balancers** under the **Load balancing** section of the left menu.  Select the ALB you created and look for the **DNS Name** listed in the Description tab.  

![ALB DNS Name](images/bonus-alb-dns.png)

Open the [API Key Management Portal](http://www.interstella.trade/getkey.html) in a new tab.  If you're not already logged in, you'll need to login with the username and password you created during the Workshop Setup.  

Enter the ALB endpoint in the text field using the following format:

<pre>
http://<b><i>ALB_ENDPOINT_DNS_NAME</i></b>:5000/order/
</pre>

Click on **Subscribe to monolith resources** to subscribe to the Orders SNS topic.  

![SNS Subscription](images/bonus-alb-sns-sub.png)

Once the endpoint is subscribed, you should start seeing orders POST in CloudWatch Logs.  You'll notice many GET requests in your log stream.  Those are the ALB health checks.  Those were left in to confirm traffic between the ALB and container(s). 

6\. Let's update the ECS Service's desired task count to introduce another instance of the logistics platform container behind the ALB.  

Navigate to the ECS dashboard, click on **Clusters** in the left menu, and click on the workshop cluster. 

![Select ECS cluster](images/bonus-cluster.png)

Select the ECS Service you created in the **Services** tab, and click **Update**.

![Update ECS Service](images/bonus-ecs-service-update.png)

Edit **Number of tasks** to be **2**.

![Update ECS Service task count](images/bonus-ecs-service-update-count.png)

No other changes are necessary, so keep clicking **Next Step** until Step 4, where you'll click **Update Service**.  Once the update's completed, click **View Service** and you'll notice the **Desired Count** is now **2** with a **Running Count** of **1**.

![Review update](images/bonus-ecs-service-updated-1.png)

Once the 2nd container is launced, you'll see the **Running Count** show as **2**.  You'll need to click the refresh button near the upper right hand corner of the table to see this change. 

![Review update complete](images/bonus-ecs-service-updated-2.png)

### Checkpoint: 
In this bonus lab, you implemented an ALB as a way to distribute incoming HTTP orders to multiple instances of Interstella 8888's logistics platform container.  

* * *

### Additional Challenge

If you've got extra time and don't feel like rushing off just yet, try implementing ECS [Service Auto Scaling](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html). 

* * *

## Finished! Please fill out evaluation cards!

Congratulations on completing the labs or at least giving it a good go.  Thanks for helping Interstella 8888 regain it's glory in the universe!  If you ran out of time, do not worry, we are working on automating the admin side of the workshop, so you will be able to run this lab at your own pace at home, at work, at local meetups, on vacation...ok, maybe that's taking it a bit far.  If you're interested in getting updates, please complete the feedback forms and let us know.  Also, please share any constructive feedback, good or bad, so we can improve the experience for customers like yourselves.

Interstella 8888 has bigger goals of refactoring their software to run as a microservices architecture.  If you liked this workshop and want to take on the challenge of breaking up the logistics platform into to microservices, check out Workshop 2 in the series - Interstella 8888: Monolith to Microservices with Amazon ECS.

* * * 

## Workshop Cleanup

This is really important because if you leave stuff running in your account, it will continue to generate charges.  Certain things were created by CloudFormation and certain things were created manually throughout the workshop.  Follow the steps below to make sure you clean up properly.  

1. Delete any manually created resources throughout the labs, e.g. ALBs (if you got to the bonus lab).  Certain things like task definitions do not have a cost associated, so you don't have to worry about that.  If you're not sure what has a cost, you can always look it up on our website.  All of our pricing is publicly available, or feel free to ask one of the workshop attendants when you're done. 
2. Delete any container images stored in ECR, delete CloudWatch logs groups, and delete ALBs and target groups (if you got to that lab)
3. Delete the CloudFormation stack launched at the beginning of the workshop to clean up the rest.  If the stack deletion process encountered errors, look at the Events tab in the CloudFormation dashboard, and you'll see what steps failed.  It might just be a case where you need to clean up a manually created asset that is tied to a resource goverened by CloudFormation.  