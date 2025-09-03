#!/bin/bash

echo "🚀 Testing your optimized AI models for Continue..."
echo ""

echo "Testing Llama 3.2 1B (Ultra Fast):"
time ollama run llama3.2:1b "Write a C# class property for email validation" | head -5
echo ""

echo "Testing CodeGemma 2B (Coding Expert):"
time ollama run codegemma:2b "// C# method to hash password" | head -5
echo ""

echo "Testing Phi-3.5 Mini (Balanced):"
time ollama run phi3.5:3.8b "Create a C# async method" | head -5
echo ""

echo "🎯 All models are ready! Now restart VS Code and use Continue extension."
echo "💡 Your fastest model is Llama 3.2 1B - it should be lightning fast!"
