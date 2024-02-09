# Use an official Jupyter image as a parent image
FROM jupyter/base-notebook:latest

# Install any needed packages specified in requirements.txt
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Run jupyter notebook when the container launches
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
