Create codecommit - take melange
Create IAM creds

Create codebuild
ENV AWS_ACCOUNT_ID acctid
ENV IMAGE_REPO_NAME name of your repo 

Modify IAM role created^
`{
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:GetAuthorizationToken",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": "*",
      "Effect": "Allow"
    },
s`

CFN Create ECR
Check in Dockerfile
Check in buildspec.yml
generic buidlspec, 1 codbuild per service

Push dev

version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - $(aws ecr get-login --no-include-email --region $AWS_DEFAULT_REGION)
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...          
      - docker build -t $IMAGE_REPO_NAME:latest .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG      
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG




# Real stuff

## Overview
Welcome to the Interstella 8888 team!  Interstella 8888 is an intergalactic trading company that deals in rare resources.  Business is booming, but we're struggling to keep up with orders mainly due to our legacy logistics platform.  We heard about the benefits of containers, especially in the context of microservices and devops. We've already taken some steps in that direction, but can you help us take this to the next level? 

We've already moved to a microservice based model, but are still not able to develop quickly. We want to be able to deploy to our microservices as quickly as possible while maintaining a certain level of confidence that our code will work well. This is where you come in.

If you are not familiar with DevOps, there are multiple facets to the the word. One focuses on organizational values, such as small, well rounded agile teams focusing on owning a particular service, whereas one focuses on automating the software delivery process as much as possible to shorten the time between code check in and customers testing and providing feedback. This allows us to shorten the feedback loop and iterate based on customer requirements at a much quicker rate. 

In this workshop, you will take Interstella's existing logistics platform and apply concepts of CI/CD to their environment. To do this, you will create a pipeline to automate all deployments using AWS CodeCommit or GitHub, AWS CodeBuild, AWS CodePipeline, and AWS CloudFormation. Today, the Interstella logistic platform runs on Amazon EC2 Container Service following a microservice architecture, meaning that there are very strict API contracts that are in place. As part of the move to a more continuous delivery model, they would like to make sure these contracts are always maintained.

### Requirements:  
* AWS account - if you don't have one, it's easy and free to [create one](https://aws.amazon.com/)
* AWS IAM account with elevated privileges allowing you to interact with CloudFormation, IAM, EC2, ECS, ECR, ALB, VPC, SNS, CloudWatch, AWS CodeCommit, AWS CodeBuild, AWS CodePipeline
* A workstation or laptop with an ssh client installed, such as [putty](http://www.putty.org/) on Windows; or terminal or iterm on Mac
* Familiarity with Python, vim/emacs/nano, [Docker](https://www.docker.com/), AWS and microservices - not required but a bonus

### Labs:  
These labs are designed to be completed in sequence, and the full set of instructions are documented below.  Read and follow along to complete the labs.  If you're at a live AWS event, the workshop attendants will give you a high level run down of the labs and be around to answer any questions.  Don't worry if you get stuck, we provide hints and in some cases CloudFormation templates to catch you up.  

* **Workshop Setup:** Setup working environment on AWS  
* **Lab 1:** Containerize Interstella's logistics platform
* **Lab 2:** Deploy your container using ECR/ECS
* **Lab 3:** Break down the monolith to microservices and deploy using ECR/ECS
* **Bonus Lab:** Scale your microservices with ALB 


### Conventions:  
Throughout this workshop, we provide commands for you to run in the terminal.  These commands will look like this: 

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_DNS_NAME</i></b>
</pre>

The command starts after the $.  Text that is ***UPPER_ITALIC_BOLD*** indicates a value that is unique to your environment.  For example, the ***PRIVATE\_KEY.PEM*** refers to the private key of an SSH key pair that you've created, and the ***EC2\_PUBLIC\_DNS\_NAME*** is a value that is specific to an EC2 instance launched in your account.  You can find these unique values either in the CloudFormation outputs or by going to the specific service dashboard in the AWS management console. 

### Workshop Cleanup:
You will be deploying infrastructure on AWS which will have an associated cost.  Fortunately, this workshop should take no more than 2 hours to complete, so costs will be minimal.  When you're done with the workshop, follow these steps to make sure everything is cleaned up.  

1. Delete any manually created resources throughout the labs.  Certain things do not have a cost associated, and if you're not sure what has a cost, you can always look it up on our website.  All of our pricing is publicly available, or feel free to ask one of the workshop attendants when you're done. 
2. Delete any container images stored in ECR, delete CloudWatch logs groups, and delete ALBs (if you get to that lab) 
3. Delete the CloudFormation stack launched at the beginning of the workshop to clean up the rest.

* * * 

### Lab 1 - Offload the application build from your dev machine

In this lab, you will start the process of automating the entire software delivery process. The first step we're going to take is to automate the Docker container builds and push the container image into the EC2 Container Registry. This will allow you to develop and not have to worry too much about build resources. We will use AWS CodeCommit and AWS CodeBuild to automate this process. 

We've already separated the code in the application, but it's time to move the code out of the monolith repo so we can work on it quicker. As part of the bootstrap process, CloudFormation has already created an AWS CodeCommit repository for you. It will be called {EnvironmentName}-spice. We'll use this repository to break apart the spice microservice code from the monolith. 

1\. Get details to check in and use your AWS CodeCommit repository

In the AWS Management Console, navigate to the AWS CodeCommit dashboard. 

![CodeCommit Click Get Started](3-2-codecommitclickgetstarted.png)

![CodeCommit Click Create Repo](3-1-codecommitclickcreaterepo.png)

Name the repository **ecs-interstella-workshop-melange-service**. Enter the following in for the description:

<pre>
This repository was created as part of the ecs-interstella-workshop to learn how to create a CI/CD pipeline in AWS for ECS.
</pre>

![CodeCommit Create Repo](3-3-codecommitcreaterepo.png)

2\. When the **Connect to your repository** menu appears, choose **HTTPS** for the connection type to make things simpler for this lab. Then follow the **Steps to clone your repository**. Click on the **IAM User** link. This will generate credentials for you to log into CodeCommit when trying to check your code in. You can also use SSH to access CodeCommit. Simply follow the SSH instructions.

![CodeCommit Connect Repo](3-4-codecommitcreateiam.png)

Scroll down to the **HTTPS Git credentials for AWS CodeCommit** section and click on **Generate**. 

![Codecommit HTTPS Credentials](3-5-codecommitgeneratecreds.png)

Save the **User name** and **Password** as you'll never be able to get this again.

3\. Create an AWS CodeBuild Project.

*You may be thinking, why would I want this to automate when I could just do it on my local machine. Well, this is going to be part of your full production pipeline. We'll use the same build system processas you will for production deployments. In the event that something is different on your local machine as it is within the full dev/prod pipeline, this will catch the issue earlier. You can read more about this by looking into **Shift Left**.*

In the AWS Management Console navigate to the AWS CodeBuild console. If this is your first time using AWS CodeBuild in your region, you will have to click **Get Started**. Otherwise, create a new project.

On the **Configure your project** page, enter in the following details:
Project Name: build-melange-service
Source Provider: AWS CodeCommit
Repository: ecs-interstella-melange-service
Type: No Artifacts
Role Name: codebuild-build-melange-service-service-role
![CodeBuild Create Project](png)
Click Continue.
Click Save.

4\. Modify the newly created IAM Role to allow access to ECR.

In the AWS Management Console, navigate to the AWS IAM console, update the service role to include:
<pre>

`{
  "Action": [
    "ecr:BatchCheckLayerAvailability",
    "ecr:CompleteLayerUpload",
    "ecr:GetAuthorizationToken",
    "ecr:InitiateLayerUpload",
    "ecr:PutImage",
    "ecr:UploadLayerPart"
  ],
  "Resource": "*",
  "Effect": "Allow"
},`

</pre>

The entire JSON should look like this:
`{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:logs:us-east-2:123456789012:log-group:/aws/codebuild/build-melange-service",
                "arn:aws:logs:us-east-2:123456789012:log-group:/aws/codebuild/build-melange-service:*"
            ],
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        },
        {
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:CompleteLayerUpload",
                "ecr:GetAuthorizationToken",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ],
            "Resource": "*",
            "Effect": "Allow"
        },
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::codepipeline-us-east-2-*"
            ],
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:GetObjectVersion"
            ]
        },
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:codecommit:us-east-2:123456789012:ecs-interstella-workshop-melange-service"
            ],
            "Action": [
                "codecommit:GitPull"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameters"
            ],
            "Resource": "arn:aws:ssm:us-east-2:123456789012:parameter/CodeBuild/*"
        }
    ]
}`

5\. Copy the commands needed to login, tag, and push to ECR

In the AWS Management Console, navigate to the Amazon EC2 Container Service console. On the left, click on Repositories. You'll see a number of repositories that have already been created for you. Choose the one for melange and click on *View Push Commands* to get the commands to login, tag, and push to this particular ECR repo.

![ECR Instructions](png)

6\. Update the service code and check in!

In the AWS Management Console, navigate to the AWS EC2 dashboard. Click on **Instances** in the left menu.  Select either one of the EC2 instances created by the CloudFormation stack and SSH into the instance.  

*Tip: If your instances list is cluttered with other instances, type the **EnvironmentName** you used when running your CloudFormation template into the filter search bar to reveal only those instances.*  

![EC2 Public IP](1-ec2-IP.png)

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_IP_ADDRESS</i></b>
</pre>

If you see something similar to the following message (host IP address and fingerprint will be different, this is just an example) when trying to initiate an SSH connection, this is normal when trying to SSH to a server for the first time.  The SSH client just does not recognize the host and is asking for confirmation.  Just type **yes** and hit **enter** to continue:

<pre>
The authenticity of host '52.15.243.19 (52.15.243.19)' can't be established.
RSA key fingerprint is 02:f9:74:ef:d8:5c:19:b3:27:37:57:4f:da:37:2b:e8.
Are you sure you want to continue connecting (yes/no)? 
</pre>

5\. Clone workshop repo and commit one microservice to your repo

Once logged in, your new repository and the workshop repository. Go back to the AWS CodeCommit console, click on your repository, and then copy the command to clone your empty repository.

<pre>
$ git clone https://git-codecommit.*your_region*.amazonaws.com/v1/repos/*ecs-interstella-workshop-melange-service*

$ git clone https://github.com/interstellaworkshop
</pre>

Copy one of the microservice folder contents into your new service. 

*You are now separating one part of the repository into another so that you can commit direct to the specific service. Similar to breaking up the monolith application in lab 2, we've now started to break the monolithic repository apart.*

<pre>
$ cp -R ecs-interstella-workshop/lab3/melange/ ecs-interstella-workshop-melange-service/
$ cd ecs-interstella-workshop-melange-service
$ git add -A
$ git commit -m "Splitting melange service into its own repo"
$ git push origin dev
</pre>

If we go back to the AWS CodeCommit dashboard, we should now be able to look at our code we just committed.



7\. Add a file to instruct AWS CodeBuild on what to do.

AWS CodeBuild uses a definition file called a buildspec.yml file. The contents of the buildspec will determine what AWS actions CodeBuild should perform. The key parts of the buildspec are Environment Variables, Phases, and Artifacts. 

At Interstella, we want to follow best practices, so there are 2 requirements:
1. We don't use the *latest* tag for Docker images. We have decided to use the Commit ID from our source control instead as the tag so we know exactly what image was deployed.
2. We want this buildspec to be generalized to multiple environments but use different CodeBuild projects to build our Docker containers. You have to figure out how to do this

Again, one of your lackeys has started a buildspec file for you, but never got to finishing it. Add the remaining instructions to the buildspec.yml.draft. Here are some links to the documentation and hints:

Log into ECR: http://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html
*disregard the --no-include-email portion*
Building a Docker image: https://docs.docker.com/get-started/part2/#build-the-app
Available Environment Variables in CodeBuild:  http://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

8\. Check in your new file into the AWS CodeCommit repository.
<pre>
$ git add -A
$ git commit -m "Adding in support for AWS CodeBuild"
$ git push origin dev
</pre>

9\. Test your build.

In the AWS CodeBuild console, choose the melange project and build it. Select the **dev** branch and the newest commit should populate automatically. Your commit message should appear as well. Then click **Start Build**. 

If all goes well, you should see a lot of successes and your image in the ECR console. Inspect the **Build Log** if there were any failures. You'll also see these same logs in the CloudWatch Logs console. 

![Successes in CodeBuild](png)

10\. Link AWS CodeCommit and AWS CodeBuild to automate a build of your dev branch.
**Can I do pull request and build?**

### Lab 2 - Set up a pipeline to automate the software release process

In this lab, you will build upon the process that you've already started by introducing an orchestration layer to control builds, deployments, and more. To do this, you will create a pipeline to automate all deployments using AWS CodeCommit or GitHub, AWS CodeBuild, AWS CodePipeline, and AWS CloudFormation. Today, the Interstella logistic platform runs on Amazon EC2 Container Service following a microservice architecture, so we will be deploying to an individual service. 

1\. Create a master branch and check in your new code including the buildspec.

Log back into your EC2 instance and create a new branch in your CodeCommit repository.
<pre>
#Todo: Create branch code in git
</pre>

2\. Create an AWS CodePipeline and set it up to listen to AWS CodeCommit. 

In the AWS Management Console, navigate to the AWS CodePipeline console. Click on **Create Pipeline**.

*Note: If this is your first time visiting the AWS CodePipeline console in the region, you will need to click "**Get Started**"*

Name your pipeline the same as the AWS CodeCommit Repository. In the example, we would name the Pipeline "**ecs-interstella-workshop-melange-service**". Click Next.

![CodePipeline Name](3-6-codepipelinename.png)

For the Source Location, choose **AWS CodeCommit**. Then, choose the repository you created as in Step 1. If using GitHub, choose **GitHub** and log in. AWS CodePipeline will automatically populate your repositories from GitHub.

*Here, we are choosing what we want AWS CodePipeline to monitor. Using Amazon CloudWatch Events, AWS CodeCommit will trigger when something is pushed to a repo.*

![CodePipeline Source](3-7-codepipelinesource.png)

Next, configure the Build action. Choose **AWS CodeBuild** as the build provider. Click **Create a new build project** and name it **ecs-interstella-workshop-melange-service**.

![CodePipeline Build](3-8-codepipelinebuildproject.png)

Scroll down further. In the Environment: How to build section, select Ubuntu as the operating system, Python as the runtime, and python 2.7 as the version. Once confirmed, ensure **Create a service role in your account** is selected and leave the name as default. When you're done, choose **Save build project**. AWS CodeBuild will create a project for you which should take about 10 seconds. Once it's done, click **Next Step**.

![CodePipeline Build Pt2](3-9-codepipelinebuildprojectpt2.png])

![CodePipeline Deploy](3-10-codepipelinedeploy.png)
*Todo: CodePipeline Deploy to ECS direct.*

In the next step of creating your pipeline, we must give AWS CodePipeline a way to access artifacts and dependencies to pull. We could use the default service role that gets automatically created for this, but we'll create a specific role for this specific pipeline. Leave the Role Name blank and click **Create Role**. 

![CodePipeline Role Creation](3-11-codepipelinerolecreation.png)

You will be automatically taken to the IAM Management Console to create a service role. Choose **Create a new IAM Role** and name it **ecs-interstella-workshop-melange-service-codepipeline-role** as you did above. Click **Allow** to create the role and return to AWS CodePipeline. Click **Next Step**
![CodePipeline Role IAM](3-12-codepipelineroleiam.png)

When you return to the AWS CodePipeline Console, click in the blank dialog box for Role Name and choose the newly created IAM Role. Click **Next Step**

![CodePipeline Role Select](3-13-codepipelineroleselect.png)

Review your pipeline and click **Create pipeline**.

### Checkpoint:  
At this point you have a pipeline ready to listen for changes to your repo. Once a change is checked in to your repo, CodePipeline will bring your artifact to CodeBuild to build the container and check into ECR. AWS CodePipeline will then deploy your application into ECS using the existing task definitions

### Lab 3 - Implement Automated Testing
Now that we've automated the deployments of our application, we want to make sure we're automating the testing of the application as well. We've decided that as a starting point, all Interstella deployments will require a minimum of 1 unit test to make the changes minimal for developers. 

Since we know the existing API contracts for our microservices, we will be ensuring that when we pass in proper data, the request will fulfill. Otherwise, it should fail.

1\. Create another stage for testing in your existing pipeline

Navigate to the AWS CodePipeline dashboard and choose your pipeline. Edit the pipeline and add in a Test stage. 





Here is a reference architecture for what you will be implementing in Lab 1:
![Lab 1 Architecture](lab1.png)

6\. Now that we have a branch to test, let's make sure it builds locally. In this case, we're creating a Docker image. 

<pre>
$ docker build -t melange-microservice:test .
$ docker run -it 
$ log into ECR and push
</pre>

This should give you output similar to: 

CodeCommit: