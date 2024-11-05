# Langchain Quick Start Guide

## Welcome to Austin LangChain!

This guide is designed to streamline your setup process, ensuring you're ready to dive into our in-person labs. Follow these instructions to familiarize yourself with the key resources we frequently use. This preparation will enhance your ability to actively participate and engage with the session's content.

## Inference Layer Setup

Inference allows AI models to interpret and respond to various data types, or *modalities*, to name a few: **Text-to-Text (NLP)**, **Speech-to-Text (STT)**, **Text-to-Speech (TTS)**, and **Speech-to-Speech (STS)**. Advanced *multimodal* models can combine these to create rich, context-aware responses across formats. Accessing these capabilities can be done through paid APIs or by running open-source models on local GPU and CPU hardware.

### Inference Cloud Provider Way

Here are some notable Inference API providers:

| Provider              | Link                                      |
|-----------------------|-------------------------------------------|
| Anthropic (Claude 3)  | [Anthropic](https://www.anthropic.com/api)|
| xAI (Grok)            | [xAI](https://x.com/)                     |
| OpenAI (GPT-4)        | [OpenAI](https://platform.openai.com/)    |
| Google (Gemini)       | [Google](https://aistudio.google.com/)    |

### Private Open Source Way (Ollama)

Ollama is our top choice for local model deployment, offering flexibility across macOS, Windows, and Linux. With strong community support and Docker compatibility, Ollama simplifies deploying, managing, and customizing models. It includes a vast model library for tasks like NLP, code generation, and data analysis, so you can adapt AI to your exact needs. The only limit is your hardware and model size: larger models demand more powerful setups, making hardware specs and model parameters key considerations for performance. For guidance, the [Ollama Github Repo](https://github.com/ollama/ollama) provides setup instructions, and there are many tutorials on YouTube and the web to help you get familiar with it.

## Open Web UI

**Open Web UI** is a free, open-source interface that integrates smoothly with LangChain agents with pipeline support. Built as a Progressive Web App (PWA) with authentication support, it’s accessible from any device. Designed for flexibility, it lets you connect to inference API endpoints from any source, whether they run on your local GPU hardware or on cloud-based providers, giving you powerful, on-demand access to advanced AI tools wherever you need them.

### Tailored Pipelines & LangChain Integration

With Open Web UI, you can set up tailored pipelines to seamlessly integrate your LangChain agents. Whether it’s retrieving web data, connecting to your notes, or querying a database with natural language, you can build workflows that meet your specific needs. These pipelines make it simple to combine different AI functions, and fully control how they interact.

### Easy Deployment with Docker Support

Open Web UI offers Docker support, allowing you to deploy it quickly on your own servers or cloud platforms. This flexibility means you can set up Open Web UI for personal use, or make it accessible to others, such as family members or team members if you’re running a business.

### Why Use Open Web UI?

Think of Open WebUI as your AI ‘command center.’ With flexible deployment options and support for hardware scaling, including GPU acceleration through Docker and Kubernetes, it allows you to centralize AI workflows, connect inference endpoints, and tailor configurations for personal or collaborative use, all from a single, user-friendly interface that you can acess from anywhere.

For more details, check out the [Open Web UI documentation](https://docs.openwebui.com/).

![Open Web UI](https://docs.openwebui.com/assets/images/demo-d3952c8561c4808c1d447fc061c71174.gif)


### LangSmith

[LangSmith](https://www.langchain.com/langsmith), developed by LangChain, is a DevOps platform that provides visibility into the sequence of calls in your LangChain applications as they interact with AI models. This visibility is essential for debugging and testing.

LangSmith is especially useful for tracking and optimizing your LangChain applications before deployment. It’s a paid service, so you’ll need an account and an API key to use its features.

Here's a quick demo of LangSmith in action:

![LangSmith Demo](https://miro.medium.com/v2/resize:fit:2000/1*4kgFH6MqBldGgbxWWYP51A.gif)


## Google Colab
Google Colab is a free cloud-based platform that lets you write and execute Python code through your browser. At Austin LangChain, we use Colab to write, share, and explain code in real-time during our labs.

This approach allows everyone to follow along with the concepts we're learning about LangChain, without needing any special setup on their personal computers. It's an ideal tool for collaborative learning and experimentation, ensuring that everyone, regardless of their hardware, can participate fully in our sessions.

Setting up a Google Colab account is straightforward and only takes a few steps:

1. **Google Account:** Ensure you have a Google account. If not, you can create one [here](https://accounts.google.com/signup).

2. **Access Google Colab:** Visit [Google Colab](https://colab.research.google.com) and sign in with your Google account credentials.

3. **Open a Notebook:** Once logged in, you can open an existing notebook from Google Drive, GitHub, or by uploading a file. To test if your setup works and familiarize yourself with our labs, follow this link to one of our early labs: [LangChain 101-1: Streamlit Streaming Lab](https://colab.research.google.com/github/colinmcnamara/austin_langchain/blob/main/labs/LangChain_101/101-1-streamlit_streaming.ipynb).

## Setting Up Environment Variables (Keys / Secrets)
In our projects, we frequently utilize environment variables, such as the OpenAI API Key, for accessing OpenAI models. Depending on the lab, there will be two environment types in which we will often use keys:

1. Google Colab
2. Your own machine

### Google Colab

Setting up secrets in Colab is easy. Simply click on the key icon in the sidebar and follow the instructions. Note that once you add a key, it persists across all your Colab notebooks in your Google account, which is highly beneficial.

![Google Colab Key](./quick_start_assets/colab_key.png)

Note that you can access secrets in your notebooks like this:

```
from google.colab import userdata
openai_api_key = userdata.get('OPENAI_API_KEY')
```

During our labs, we've already got these steps covered in our notebooks! You'll jump straight into the action, playing with the latest and greatest LangChain tech that we've been tinkering with at Austin LangChain. It's like having a VIP pass to the AI playground! 🚀✨

### Your Own Machine

Alternatively, If you’re pulling code from a repo and want to run it locally, you can set up your secrets in your own machine in accordance to your operating system.

There's plenty of detailed tutorials out there for this. Here's some examples depending on your os:

#### Mac OS / Linux

Add environment variables directly in the terminal:
```bash
export API_KEY="your_value"
export DB_PASSWORD="your_value"
```

#### Windows

Set environment variables in Command Prompt:
```cmd
set API_KEY=your_value
set DB_PASSWORD=your_value
```

## Docker

Docker is widely celebrated for its ability to simplify and accelerate development by packaging applications and their dependencies into portable containers. This containerization ensures that the same setup runs seamlessly across your local, testing, and production environments, eliminating the headaches of inconsistent configurations. It’s a tool we frequently rely on at Austin LangChain to make deployments smooth and consistent.

In fact, many AI applications come ready with Docker images and Dockerfiles, making it easy to spin up complex environments with just a few commands.  If you're new to it, take a look at our [Intro to Docker](../../labs/LangChain_103/103-1-docker_introduction.md) tutorial or checkout Docker's very detailed documentation [here](https://docs.docker.com/get-started/). It's a technology that's well worth learning!


### Windows and Mac OS

* Just install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for easy setup.

Docker Desktop includes everything you need to start working with Docker:
*	**Docker Engine and CLI**: The core services for building, running, and managing containers.
*	**Docker Compose**: A tool for defining and running multi-container applications, useful for orchestrating complex setups with multiple services.
* **User Interface**: An intuitive GUI to manage containers, images, and volumes directly, making it easier for beginners to get comfortable with Docker.


### Linux

For Linux, the Docker CLI through Docker Engine is typically the best option—it’s lightweight and efficient for native container management. Docker Desktop is available for Linux, but it runs in a VM, which might not be necessary for most users.

* See [Docker Engine installation instructions](https://docs.docker.com/engine/install/) for your specific Linux distribution.
