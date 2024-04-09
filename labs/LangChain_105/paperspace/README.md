# Using the Serge Application with Paperspace

This README contains quick guide instructions for running the [Serge-Chat](https://github.com/serge-chat/serge) application using Paperspace Deployments. The default launch settings will serve the application on a NVIDIA A100-80G. For more (i.e. cheaper) options, you can get the relevant machine codes from the [Paperspace Machines documentation](https://docs.digitalocean.com/products/paperspace/machines/details/pricing/) page. 

To follow this tutorial, you will need a Paperspace account with a payment method on file. 

Link to slides for this subdir: https://docs.google.com/presentation/d/152VfrQlDaRGePjOqRFvVGr8xCFmUIcEepFbnVSxfpAU/edit#slide=id.g210370ff760_0_420

## How to launch the Deployment

1. Go to console.paperspace.com, and navigate to a Team and Project of your choice. For most of you, that will be the first project you make in your Personal Workspace
2. Click the Deployments tab, and then click "Create"
3. Select your GPU Machine, we suggest the A100-80G
4. Name your deployment accordingly. we are going to name ours "serge"
5. For the "Image" section, leave the "Public container registry" toggled, and fill in the field "Image" with "ghcr.io/serge-chat/serge:latest"
6. Set the port to 8008. Additionally, we can also set up replicas and autoscaling if we anticipate a lot of traffic on our application
7. Finally, click the "View advanced options" button to turn on any Health checks we may want for our application. None of these are needed to run this application at this time. 
8. Review the pricing summary before proceeding, and click to Deploy to launch the application. 
9. Afterwards, you will be redirected to the Deployment's homepage. There, we can get the link to the API endpoint URL, view logs, and make changes to our Deployment's settings. Importantly, it's critical that you set a timer for how long to run the Deployment at this time. This will prevent you from accidentally getting charged after this session, as the Deployments do not automatically disable. We can also shut them down manually at any time in the settings or in the Project's Deployments tab

Alternate format for the fields can be found in `Paperspace.json` 


## Using the Serge Chat application

1. Click the API endpoint URL to access the Web UI.
2. From here, we need to download LLM model checkpoints to use with the app. In the interest of time, i suggest a smaller model to start with. Other models can be downloaded in the background while using the application
3. Once your model has downloaded, we can set various chat settings that should be very familiar to LLM developers like temperature, context length, etc. Make these settings and then launch the chat 
4. Chat with the model! 