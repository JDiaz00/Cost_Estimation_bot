#!/usr/bin/env python3
"""
Executable script to run the Construction Cost Estimation Chatbot
"""
import asyncio
import sys
import os

# Add the current directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    asyncio.run(main()) 