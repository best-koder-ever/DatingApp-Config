#!/bin/bash

echo "🚀 Starting Ollama with GPU optimizations for small models..."

# Kill any existing Ollama processes
pkill -f ollama

sleep 2

# Enhanced GPU settings for small models (1B-3B parameters)
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_GPU_LAYERS=999
export OLLAMA_GPU_MEMORY_FRACTION=0.9
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_ORIGINS="*"

# Small model optimizations - higher context for better performance
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=2

# Start Ollama service
ollama serve &

sleep 3

echo "⚡ GPU Status:"
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader,nounits

echo ""
echo "� Ready! Your optimized models:"
echo "   • Llama 3.2 1B (1.3GB) - Ultra fast"
echo "   • CodeGemma 2B (1.6GB) - Coding specialist" 
echo "   • Phi-3.5 Mini (2.2GB) - Best balance"
echo ""
echo "💡 Use Continue extension with these models for blazing fast coding!"
