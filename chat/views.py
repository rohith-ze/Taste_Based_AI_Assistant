from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from spotify_agent.agent_call import agent_executor as spotify_agent_executor
from movie_agent.agent_main import agent_executor as movie_agent_executor

# Create your views here.

@csrf_exempt
def spotify_agent_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
            if not user_input:
                return JsonResponse({'error': 'No user input provided'}, status=400)
            
            response = spotify_agent_executor.invoke({'input': user_input})
            return JsonResponse({'response': response.get('output', '')})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Only POST requests are supported'}, status=405)

@csrf_exempt
def movie_agent_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
            if not user_input:
                return JsonResponse({'error': 'No user input provided'}, status=400)
            
            response = movie_agent_executor.invoke({'input': user_input})
            return JsonResponse({'response': response.get('output', '')})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Only POST requests are supported'}, status=405)