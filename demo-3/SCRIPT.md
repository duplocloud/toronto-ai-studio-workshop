## Demo 3

//TODO: Make sure stands is installed and working.

In Demo 3, we're connecting HelpDesk Chat with AI. We'll be using Strands Agents. 
- Developed by AWS, Released this past May 2025
- Used by
    - Amazon Q Developer
    - AWS Glue
- Has Agentic Capabilities
- Tool Support
- Workflows/
- Many Model Providers
- Native support for Bedrock Models


Our team has been using Strands Agents since it's release in our products, we've found it easy to use, easy to extend, and thoughtfully designed. It strikes a great balance between simplicity and feature.  Today we'll use it to create a small application using it.

Let's go to Visual Studio Code and Navigate to the demo-3 folder. Inside the demo-3 folder, you're see the same files we've been working with. Let's open the main.py

//TODO: we need to configure the Environment varables.

On, line 32, is the echo code from the first demo-1. We're going to replace this code with our Strands Agent code. Strands should already be installed.

First lets delete the echo code and add setup the Strands Agent.

First thing we need to do is setup the Authentication via Boto

//TODO: Get the creds, for Amazon

The first thing we want to do is get the conversation history from the payload. I've created a function that already does this. We can use it: It's called `get_conversation_history`. Let's take a look at what is does.

//TODO: make sure the imports already exisit.
conversation_history = get_conversation_history(payload)

Now that we have the conversation history lets setup the session from Boto:

//TODO: need the auth story figured out.
        session = boto3.Session( # If using temporary credentials
            region_name='us-east-2',
            profile_name='test10'  # Optional: Use a specific profile
        )

Now that we've go the authentication in place, let's pass it to our BedRock Model. I've created a function for this. It's called `get_bedrock_claude_3_5`

bedrock_model = get_bedrock_claude_3_5(session)

Now that we have the bedrock model setup, let's move to getting the agent setup.

We're using the strands agent. So we need to add the strands Agent class. It has 2 parameters we need to set:
The model and the messages. Let's add the bedrock_model. Now lets add our conversation history. We need to make sure that we are capturing the agent variable.

        # Create echo response
        agent = Agent(
            model=bedrock_model,
            messages=conversation_history
        )

How that we have our agent configured with the model and the conversation history, let's pass the content (user message) we receive into it. We do that by `agent(content)` and capturing a response `agent_response`. The agent_response comes in an structure with multiple layers, so I've created a function to just get the message, it's called `get_agent_response()`.

        agent_response = agent(content)
        ai_response = get_agent_response(agent_response)

The last thing we want to do, is return that response. We do that by passing it to our `Endpoint.success` method. We just replace the content variable with our ai_response method.


response_payload = Endpoint.success(
    content=ai_response,
    payload=payload
)

Now that we have this all set up. Let's test this locally, to ensure it's setup.

First let's start the api. Like before, I've created a start.sh script. Making sure that we are still in the demo-3 folder, let's run the command `./start/sh`. If all is well the server should start.

Now lets hit the endpoitn, I've created a shell script, like the others `./test-api.sh` for this. The shell script asks the llm to write a short poem about a cat. If all is working, we'll set a beautiful cat poem back.

//Make sure everyone is getting the right poem back.

Now that we're getting a response back, it's time to deploy it.

Like before, I have another shell script for deploying. `./build-deploy.sh` Let's run this script. 

Did everyone's image build and deploy correctly?

Grab that url from the terminal, or remember your version number.

//TODO: might have to setup environement variables... maybe not, but adding it here just in case.

Before redeploy the image in Duplocloud, we need to add some Environment variables.

First, let's go to our duplo cloud instance: https://duplo.workshop05.duploworkshop.com.

When the page loads, you'll see on the left nav "AI Suite", click it. The you'll "Studio" if the studio menu isn't expanded, click on it, and you should see "Agents", lets go there. This will bring you to the "Agents" page. Find you agent in the table and click on the 3 dots on the left, in the first column. Select Edit.Towards the bottom, you'll see Environment variables. We need to add the environment variables we used in our development environment here. When you add them, make sure the "Mandatory" toggle is enabled. If not, it doesn't deploy with that variable.

How are we doing. Do we have all the variable set?

Click the save/submit button. We should now be back to the Agents page. Lets click on the name of your agent. This will take us to the agents detail page. About a 1/3 the way donw the page, you'll see "Overview" and next to it "Meta Data". Let's go to Deployments Tab.

We need to delete the existing deployment. Click on the 3 dots again. The last optoin should be "Delete", click it. It's going to ask for confirmation. click the red confirm button.

Go back to the image tab. We see our image in the grid, but it's the old image. We need to update it. Click on the three dots again. And click on "Deploy". Don't click "Quick Depoloy" We wnat to click Advanced. This will take us to a screen to edit the image url. Underneath the Service Name, you'll see "Docker Image". Change the image path. All you need to do is go to the end of the image url and change the version to your latest version. 

Once that is done, clikc the next button. 

This will to the next view, we need to clikc the next button again. If we're missing LB Listener's we need to add that also.

//REFER to the previous documentation.

After clicking Submit. find your image in the list and clikc on the name.

This will take you to the Deployments page. On the right hand side threre should be a "Pending" Box and a "LB Status" box. We need both of these to be green.

Hopefully all of us got both boxes to turn green.

Let's navigate to the Left Navigation. Click on "AI Suite" and then down to HelpDesk and click on it.

This opens our HelpDesk chat interface.

Type something you want in the message to Agent text field.

Select your agent.

For the instance, select your agent. It should be named the same as your agent name.

Click submit. Now if all goes well, we should be a response back from our llm.

