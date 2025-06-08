# Model Management for Ansible-TinyLlama Integration

This guide explains how to download, manage, and use TinyLlama models with the Ansible-TinyLlama Integration.

## Available Models

The following TinyLlama models are supported by default:

- **tinyllama-1.1b**: Base TinyLlama 1.1B model (TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T)
- **tinyllama-1.1b-chat**: TinyLlama 1.1B model fine-tuned for chat (TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- **tinyllama-1.1b-python**: TinyLlama 1.1B model fine-tuned for Python code (TinyLlama/TinyLlama-1.1B-Python-v0.1)

You can also use any compatible model from HuggingFace by providing its full repository ID.

## Downloading Models

### Using the Convenience Script

We provide a shell script for easy model management:

```bash
# List available models
./models/download_models.sh list

# Download a model
./models/download_models.sh download tinyllama-1.1b-chat

# Download with quantization (reduces memory usage)
./models/download_models.sh download tinyllama-1.1b-chat --quantize 8bit

# Force re-download of an existing model
./models/download_models.sh download tinyllama-1.1b-chat --force

# Save to a custom directory
./models/download_models.sh download tinyllama-1.1b-chat --output /path/to/models
```

### Using Python Directly

You can also use the Python module directly:

```bash
# List available models
python -m src.llm_engine.model_download list

# Download a model
python -m src.llm_engine.model_download download tinyllama-1.1b-chat
```

### Using the Main Application

The main application also supports model management:

```bash
# List available models
python src/main.py model list

# Download a model
python src/main.py model download tinyllama-1.1b-chat
```

## Model Storage Location

By default, models are stored in the `models/` directory at the root of the project. 

You can override this location by setting the `ANSIBLE_LLM_MODEL_PATH` environment variable:

```bash
export ANSIBLE_LLM_MODEL_PATH=/path/to/models
```

## Model Quantization

Quantization reduces the memory footprint of models, making them usable on devices with limited resources:

- **4-bit quantization**: Maximum memory savings, slight quality reduction
- **8-bit quantization**: Good balance of memory savings and quality

To use quantization, add the `--quantize` option:

```bash
./models/download_models.sh download tinyllama-1.1b-chat --quantize 4bit
```

### Additional Requirements for Quantization

Quantization requires additional dependencies:

```bash
pip install bitsandbytes
```

## Using Custom or Private Models

You can use any compatible model from HuggingFace:

```bash
./models/download_models.sh download facebook/opt-125m
```

For private models, you'll need a HuggingFace access token:

```bash
./models/download_models.sh download organization/private-model --token hf_xxxxxx
```

## Troubleshooting

If you encounter issues downloading models:

1. Check your internet connection
2. Verify your HuggingFace credentials (for private models)
3. Ensure you have sufficient disk space
4. Check the logs in the terminal for error messages

For detailed debugging information, run the Python script with the debug flag:

```bash
python -m src.llm_engine.model_download download tinyllama-1.1b-chat --debug
```
