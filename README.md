# Taste-Based AI Assistant

This project is a web application that provides personalized recommendations for movies and music through a conversational AI interface. It features three distinct AI agents: a Movie Agent, a Spotify Agent, and a Couple Movie Agent, each tailored to specific use cases. The application is built with Django and utilizes LangChain, Google's Gemini models, and the Qloo API for taste-based recommendations.

## Features

### 1. Movie Agent

The Movie Agent provides personalized movie recommendations based on a user's viewing history from their Emby media server.

-   **Personalized Recommendations:** Get movie recommendations based on your Emby watch history.
-   **Genre & Language Filtering:** Filter recommendations by genre (e.g., "comedy," "drama") or language (e.g., "english," "french").
-   **Taste Analysis:** Get a summary of your movie taste and an explanation of why the recommendations are a good fit.
-   **Trending & Recent Movies:** Discover what's currently trending or recently added to your Emby server.

### 2. Spotify Agent

The Spotify Agent offers music recommendations and insights based on your Spotify listening habits.

-   **Spotify Integration:** Connects to your Spotify account to analyze your playlists, recently played tracks, and liked songs.
-   **Music Recommendations:** Get recommendations for new artists, genres, and themes based on your listening history.
-   **Qloo-Powered Insights:** Leverages the Qloo API to provide deep insights into your musical taste.

### 3. Couple Movie Agent

The Couple Movie Agent is designed for two users, providing movie recommendations that cater to both of their tastes.

-   **Joint Recommendations:** Get movie recommendations that are a good fit for both users' watch histories.
-   **Combined Taste Analysis:** Understand the intersection of your movie tastes and get recommendations that you'll both enjoy.

## Tech Stack

-   **Backend:** Django
-   **AI/LLM:**
    -   LangChain
    -   Google Generative AI (Gemini)
    -   Groq
-   **APIs:**
    -   Qloo API (for taste-based recommendations)
    -   Emby API (for movie watch history)
    -   Spotify API (for music listening history)
-   **Frontend:** HTML, CSS, JavaScript
-   **Database:** SQLite

## Project Structure

```
/
├── appfront/           # Django project for the frontend
├── chat/               # Django app for chat functionality
├── couple_agent/       # AI agent for couple movie recommendations
├── movie_agent/        # AI agent for movie recommendations
├── spotify_agent/      # AI agent for music recommendations
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Taste_Based_AI_Assistant-4.git
    cd Taste_Based_AI_Assistant-4
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory and in each agent's directory (`movie_agent`, `spotify_agent`, `couple_movie_agent`) and add the following environment variables:

    **Root `.env` file:**
    ```
    GEMINI_API_KEY=your_gemini_api_key
    QLOO_API_KEY=your_qloo_api_key
    ```

    **`movie_agent/.env` file:**
    ```
    EMBY_SERVER=your_emby_server_url
    EMBY_API_KEY=your_emby_api_key
    EMBY_USER=your_emby_username
    USER_LOCATION=your_location
    ```

    **`spotify_agent/.env` file:**
    ```
    SPOTIPY_CLIENT_ID=your_spotify_client_id
    SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
    SPOTIPY_REDIRECT_URI=your_spotify_redirect_uri
    ```

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Start the development server:**
    ```bash
    python manage.py runserver
    ```

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:8000/`.
2.  From the home page, select the AI agent you want to interact with (Movie Agent, Spotify Agent, or Couple Movie Agent).
3.  Start chatting with the agent to get recommendations and insights.

**Example Prompts:**

-   **Movie Agent:**
    -   "Recommend some movies for me."
    -   "Recommend some comedy movies."
    -   "What kind of movies do I like?"
-   **Spotify Agent:**
    -   "Get recommendations from my spotify account."
    -   "What new music should I listen to?"
-   **Couple Movie Agent:**
    -   "Recommend a movie for us to watch tonight."
