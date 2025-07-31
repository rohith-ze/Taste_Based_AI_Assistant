from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from movie_agent.agent_main import agent_executor as movie_agent_executor
from spotify_agent.agent_call import agent_executor as spotify_agent_executor
from couple_movie_agent.couple_agent import agent_executor as couple_agent_executor

def gemini_index(request):
    return render(request, 'gemini_index.html')

def movie_agent_chat(request):
    return render(request, 'movie_agent_chat.html')

@csrf_exempt
def movie_agent_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if user_message:
                response = movie_agent_executor.invoke({"input": user_message})
                agent_response = response.get("output", "No response from movie agent.")
                return JsonResponse({'response': agent_response})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def spotify_agent_chat(request):
    return render(request, 'spotify_agent_chat.html')

@csrf_exempt
def spotify_agent_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if user_message:
                response = spotify_agent_executor.invoke({"input": user_message})
                agent_response = response.get("output", "No response from spotify agent.")
                return JsonResponse({'response': agent_response})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def couple_movie_agent_chat(request):
    return render(request, 'couple_movie_agent_chat.html')

@csrf_exempt
def couple_movie_agent_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if user_message:
                response = couple_agent_executor.invoke({"input": user_message})
                agent_response = response.get("output", "No response from couple movie agent.")
                return JsonResponse({'response': agent_response})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)