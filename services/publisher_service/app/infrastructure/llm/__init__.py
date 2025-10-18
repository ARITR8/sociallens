"""
LLM Infrastructure Module

This module provides abstraction for different LLM providers.
Currently supports:
- AWS Bedrock (Claude)
- Google Gemini

Usage:
    from app.infrastructure.llm.factory import create_llm_client
    
    llm_client = create_llm_client()
    content = await llm_client.generate_content("Your prompt here")
"""

from app.infrastructure.llm.base import BaseLLMClient
from app.infrastructure.llm.bedrock_client import BedrockClient
from app.infrastructure.llm.gemini_client import GeminiClient
from app.infrastructure.llm.factory import create_llm_client

__all__ = [
    "BaseLLMClient",
    "BedrockClient",
    "GeminiClient",
    "create_llm_client",
]