## Introduction

Hello, I'm Chuck Conway. I'm an engineer on the AI Team at Duplo. 

Today, We're doing a hands on demo with Duplo Cloud AI Suite. I'll walk you through how to setup and configure our HelpDesk and show: a simple echo agent, how to use our built-in chat features to run commands on the server, and how to connect to an LLM and chat with an LLM.

If there are any questions along the way don't hesitate to ask.

## Getting Started

//TODO: Pull down the latest code for them.
//TODO: Make sure the environments on the right branch.
//TODO: CReate a script to run on all the enviornments to make sure all the tools work.
We've created a hosted Visual Studio Code Environment for each person. You are welcome to walkthrough the code with me as I demo it.


## Demo 1

The first demo is going to be very basic. It's about getting farmilar with our Visual Studio Code setup, testing that our code works and setting up an AI Agent in Duplo.

//TODO: ask Andy, how long it takes for Duplo to deploy? (Feature suggestion, have duplo notifications)

Has everyone gotten access to their Visual Studio Code? Any problems?

If there are problems, we'll address them.

Ok, everyone should be up to date and ready to go. Let's take a tour of the project.

There should be a common folder, 3 demo folders, a Dockerfile, a readme, and a requirements.txt. 

Inside the common folder is an endpoint file. This has common code to take are of parsing the payload and formating the response. 

Let's open the folder for the first demo, called demo-1. There should be main.py, a ReadMe and push-to-ecr.sh. Main.py is where all the code we'll run is located, Readme has all the steps and instructions for this part of the demo. and push-to-ecr.sh is the script we'll use to build and push our ECR.

All the steps for this

//TODO: How do we set the person's name one-time? Do we have them all run a setup script and have the script set and Environment variable? Maybe it should write that variable out to the file so if we have to refresh their environment, it's ready to go.

Let's open main.py. 

This is a basic FASTAPI setup. 

There is a health endpoint, which is required for the Duplo AI Agents, and the chat endpoint which is our HelpDesk chat connects too.

Let's take a closer look at the the chat method.

-- Endpoint class
    - Parses the payload
    - sets correct json envolope.

Let's start the server and test it out.

There is a file in the root of the demo folder called "start.py", let's run it.

First we need to active

//TODO: make sure all the shell scripts are executable.

'./start.sh'

Ok, the api is running. Let's test ti.

In the terminal let's open another shell. And run the following command:

TODO:// Make sure test-api.sh is executable.

`.test-api.sh`

Hopefully everyone see the message echoed back to them.

Anyone have any issues?

//TODO: Figure out the aws creds
//TODO: Make sure script is executable.

Ok, now that we've all got it working. The next step is to dockerize the application and deploy it to ECR. We've already created an ECR. In the demo-1 folder, you'll find a script called "push-to-ecr.sh"

//TODO: make sure their name is setup, we also have to amke sure there is only one of each name in the the class. And no special characters.

Let's run  it.

`./push-to-ecr.sh`

This script is doing two things:
1. building the docker container.
2. pushing the image to ECR.

Let's give it a few minutes to complete.

Ok, is everyone's image pushed to the cloud?

That's good! Now let's open up a browser and go to https://duplo.workshop02.duploworkshop.com

//TODO: hopefully the login story is good togo.

This is Duplo Cloud platform. What we are interested in is the AI Suite. click on it and then clikc on the Studio item. Then go to agents.


1. Build the container.
2. Push image to the container repository (ECR) (.push-to-ecr.sh)
3. .push-to-ecr.sh
    - VERSION="v24"
    - ECR_REPOSITORY_NAME="ecs-to-eks"
    - AWS_REGION="us-east-1"
    - AWS_PROFILE="test10"

4. copy the image url.
5. Open Duplo, (https://test10.duplocloud.net)
6. Sign in if needed.
7. On the left side, open the navigation and select the AI Studio and Agents navigation
//insert image here.
8. You should be on the Agents screen
9. Click the add button.
10. This will open an Add Agent Definition View
11. Let's fill it out.
    - Name: hello-world-chuck
    - Agent Type: PreBuilt
    - Paste your image url: 938690564755.dkr.ecr.us-east-1.amazonaws.com/aws-workshop-demo:v24
    - Port: 8001
    - Http Protocal: HTTP
    - No Environment Variables
    - Meta Data
    - Click Submit

12. Click on the newly created agent.
13. You'll now be on the new Agent Details.
14 Find the vertical tabs.
15. Click on the images tab
16. You should have one image. The one we added when we created the agent.
17. Click on the 3 vertical buttons, and clikc deploy. Pick Advanced.
18. Click Next, Click Next. We should be on the LB (Load Balancer) Listeners view.
19. Clikc on the add button in the right corner.
20. Add Load Balancer Listener 
    - Select Type: Application LB
    - Container Port: 8001
    - External Port: 443
    - Visibulity: Public
    - Health Check: /health
    - Backend Protocal: HTTP
    - Protocal Policy: Default is fine.
    - Select only Certification.

21. Click Add.
22. Now click "Create"
23. Find your image in the deployment list and click the name (near the bottom).
24. now on the right side you'll see "Pending" and "LB Status" once these go green then your image is deployed.
- Running should be 1/1 (green)
- LB Status should read "Ready"
25. Now that is up and running, we have to register the chat agent.

25. go back to the Agent's detail view, and clikc on the register tab.

26.Register an Agent
 - Enter Name: aws-workshop
 - InstanceId: Pick the one we just created

27. Pick the out tenant

28. just use "chat". This is the endpoint that we exposed on our Docker Image

28a. We need to wait...

29. This is the moment of truth. When the agent works.
H
