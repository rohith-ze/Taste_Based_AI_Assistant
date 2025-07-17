import requests
import json
from dotenv import load_dotenv
import os
from langchain_core.tools import tool
load_dotenv()

QLOO_API_KEY = os.getenv('QLOO_API_KEY')
BASE_URL = os.getenv('QLOO_BASE_URL')
@tool
def qloo_call(filter_type:str, filter_tags:str):
    """Access Qloo to get taste based recommendation"""
    headers= {
        "x-api-key":QLOO_API_KEY 
    }
    params = {
        "filter.type": filter_type,
        "filter.tags": filter_tags,
    }
