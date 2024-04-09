# Multi LLM LangGraph Agent with Function Calling, Context from Images, and Image Generation using Automatic1111

### Disclaimer

This lab relies on the following:

1. [Ollama](https://ollama.ai) to run LLMs locally.
2. [Llama2](https://ollama.com/library/llama2) and [Bakllava](https://ollama.com/library/bakllava) LLMs hosted on Ollama. 
3. [a custom finetuned Mistral](https://ollama.com/klcoder/mistral-7b-functioncall) LLM for function calling hosted on Ollama.
4. [a function calling Prompt Template](https://smith.langchain.com/hub/klcoder/mistral-functioncalling) hosted on [Langchain Hub](https://smith.langchain.com/hub).

While all the code in this project, the function calling prompt template, as well as the custom finetuned LLMs are provided in good faith, run them at your own risk.

We recommend you exercise caution when running the code downloaded from the Internet, or from an untrusted source.
Always run such code in an isolated environment, like ephemeral containers, virtual machines, or cloud instances.

## Running the Agent

### Install python dependencies

```bash
pip install -r requirements.txt
```

### Download and run ollama

We will use 3 local models for this exercise.

1. llama2 for casual conversation
2. bakllava for image to text conversation
3. mistral finetuned for function calling so we can correctly identify tools to use within the agent

To get started:

1. download the ollama binary
2. make it executable
3. start ollama in the background
4. download the hosted bakllava, llama2, and function calling model

```bash
curl -L https://ollama.ai/download/ollama-linux-amd64 -o ollama
chmod +x ollama
./ollama serve &>ollama.log &

./ollama pull bakllava
./ollama pull llama2
./ollama pull klcoder/mistral-7b-functioncall

./ollama list
```

### Download and setup Automatic1111 and stable diffusion model

For text to image generation, we will use Automatic1111, a stable diffusion web ui client, that also serves an API that we can call directly.  
For this exercise, we will download the [DreamShaper XL](https://civitai.com/models/112902/dreamshaper-xl) model and [4xUltrasharp](https://civitai.com/models/116225?modelVersionId=125843) rescaler.

```bash
curl -L https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/webui.sh -o webui.sh
curl -L https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/webui-user.sh -o webui-user.sh

mkdir -p models/ESRGAN models/Stable-diffusion
curl -L https://civitai.com/api/download/models/351306 -o models/Stable-diffusion/dreamshaperXL_v21TurboDPMSDE.safetensors
curl -L https://civitai.com/api/download/models/125843 -o models/ESRGAN/4xUltrasharp_4xUltrasharpV10.pt

chmod +x ./webui.sh
./webui.sh --api --listen --xformers --ckpt-dir=./models/Stable-diffusion --esrgan-models-path=/models/ESRGAN &> a1111.log &
```

### Launch Streamlit App

```bash
streamlit run app.py &> streamlit.txt
```
