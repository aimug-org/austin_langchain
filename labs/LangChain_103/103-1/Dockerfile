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
