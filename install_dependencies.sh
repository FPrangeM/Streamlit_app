#!/bin/bash

# source venv/bin/activate
source venv/bin/activate.fish

pip install -r requirements.txt

# docker build -t streamlit-app .
# docker run -p 8080:8080 streamlit-app