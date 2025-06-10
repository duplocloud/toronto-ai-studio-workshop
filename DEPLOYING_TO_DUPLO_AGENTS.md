
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