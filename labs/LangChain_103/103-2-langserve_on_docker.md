# Developing LangChain with Docker

This guide covers the steps to set up a development environment for LangChain using Docker. By the end of this guide, you will have a functional test environment for LangChain.

## Why use Docker for LangChain?

- Manage dependencies easily.
- Consistent development environment.
- Easy deployment.
- Easy testing.
- Easy collaboration.
- Easy maintenance.
- Easy scaling.

## Clone the Repository

1. Install Git.
2. Clone the repository:

```bash
git clone https://github.com/colinmcnamara/austin_langchain
git checkout -b <yourname-dev-branch>
```

## Local Development Without Docker

Export your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key_here
```
or 
```bash
cd into 
cp sample.env ~/.env
vim ~/.env
```

## Local Development With Docker

1. Navigate to the `LangChain_103/docker_dev/langserve` directory.
2. Review and edit the included Dockerfile.
3. Build the image:

```bash
docker build -t langserve_lab .
```

4. Run the image:

```bash
docker run -p 8080:8080 -it --rm --env-file ~/.env langserve_lab 
```

5. Interact with the server at http://localhost:8080 .

6. Optional:

Add a Create a new app:

```bash
langchain app add research-assistant
```

```
edit app/server.py
```

7. rebuild image
```bash
docker build -t langserve_lab .
```

8. stop image
```bash
docker stop container_id_or_name
```
9. Start
```
docker run -p 8080:8080 -it --rm --env-file ~/.env langserve_lab 
```

6. observe:
http://localhost:8080/research-assistant/playground

## Docker Commands

### Tagging and Pushing an Image to Docker Hub

1. Log in to Docker Hub:

```bash
docker login
```

2. Tag your Docker image:

```bash
docker tag langchain_lab colinmcnamara/austin_langchain:latest
```

3. Push the tagged image to Docker Hub:

```bash
docker push colinmcnamara/austin_langchain:latest
```

### Pulling an Image from Docker Hub

```bash
docker pull colinmcnamara/austin_langchain:latest
```

### Running a Container from a Pulled Image

```bash
docker run -p 8080:8080 -it --rm --env-file ~/.env colinmcnamara/austin_langchain:latest
```

## Updating a Docker Image

1. Update your application's code or dependencies.
2. Rebuild the Docker image:

```bash
docker build -t langserve_lab .
```

3. Stop and remove the old container:

```bash
docker stop container_id_or_name
docker rm container_id_or_name
```

4. Run a container from the updated image:

```bash
docker run -p 8080:8080 langserve_lab
```

## Best Practices for Development

- Use tags for versioning.
- Mount volumes for live updates:

```bash
docker run -p 8080:8080 -v $(pwd):/usr/src/app langserve_lab
```

- Automate with Docker Compose.
- Regularly clean up unused images with `docker system prune`.

