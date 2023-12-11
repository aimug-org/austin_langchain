# Docker Tutorial: Hello World Python Script

In this tutorial, we'll create a simple Python script that prints "Hello from Docker!" and then containerize it using Docker.

## Why Docker for Austin Langchain Enthusiasts?

Docker is particularly beneficial for developers building applications with Langchain because it ensures that these applications behave consistently across different environments. This is crucial for *reproducibility* — if you share your Docker container with others, they can replicate your exact setup and results. This helps us run our labs more efficiently by quickly sharing code with participants

## Docker Main Concepts

**Dockerfile**: This is a blueprint for building a Docker image. It contains a set of instructions that tell Docker how to set up the environment for an application, such as which base image to use, which files to include, and what commands to run.

**Docker Image**: An image is a static snapshot of the Dockerfile's instructions. It bundles the application code with all the necessary components like libraries, dependencies, and other resources needed to run the application.

**Docker Container**: When you start an image, it becomes a container. A container is a runnable instance of an image, providing an isolated environment for the application to run. Containers ensure consistency across multiple development, staging, and production environments, and can be started, stopped, moved, and deleted.

*Honorable Mention*

**Docker Compose**: Docker Compose is a tool for defining and running multi-container Docker applications. It allows you to configure an application's services, networks, and volumes using a YAML file. This is particularly useful for complex environments where multiple interconnected containers need coordinated management. It simplifies the process of running and connecting these containers in a single network. More info on [Docker Compose](https://docs.docker.com/compose/) here

Consult the [Docker Docs](https://docs.docker.com/guides/get-started/) for more info

## Installation

Docker Desktop is the easiest way to get Docker up and running. It bundles everything you need in one package and offers a user-friendly interface.

For installation instructions and more details, visit [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Step 1: Creating the Python Script

First, we'll write a simple Python script named `hello.py`.

```python
# hello.py
print("Hello from Docker!")
```

Save this file to your local machine in a directory of your choice.

## Step 2: Writing the Dockerfile

Next, we'll create a `Dockerfile`. This file defines the environment for running our Python script.

```shell
# Dockerfile

# This line specifies the base image for our Docker container.
# In this case, we are using the official Python 3.8 slim image, which is a lightweight version of Python.
FROM python:3.8-slim

# This line copies the file `hello.py` from the local directory to the `/app/` directory inside the container.
# The `/app/` directory will be created if it doesn't exist.
COPY hello.py /app/

# This line sets the working directory inside the container to `/app/`.
# Any subsequent commands will be executed relative to this directory.
WORKDIR /app

# This line specifies the command that will be executed when the container starts.
# In this case, it runs the `hello.py` script using the Python interpreter.
CMD ["python", "hello.py"]
```

For more info on usage, please visit the [Dockerfile reference in the docs](https://docs.docker.com/engine/reference/builder/)

## Step 3: Building the Docker Image with Docker Desktop

To build our Docker image:

1. Open a terminal
2. Navigate to the directory containing your `Dockerfile` and `hello.py` script.
3. Run the following command to build the Docker image:

```shell
docker build -t hello-world-image .
```

This command tells Docker to build an image and use the -t flag to tag it as `hello-world-image` from the `Dockerfile` in the current directory. You can name this tag whatever you want.

For more info on usage, please visit the [docker build reference in the docs](https://docs.docker.com/engine/reference/commandline/build/)

## Step 4: Running the Docker Container

After the build completes, you can run the container:

```shell
docker run hello-world-image
```

You should see the output:

```shell
Hello from Docker!
```
For more info on usage, please visit the [docker run reference in the docs](https://docs.docker.com/engine/reference/commandline/run/)