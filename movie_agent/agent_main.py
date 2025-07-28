# agent_main.py
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ._movie_tools import fetch_watched_movies, recommend_movies, summarize_movie_taste, fetch_trending_movies, fetch_recent_movies

tools = [
    fetch_watched_movies,
    recommend_movies,
    summarize_movie_taste,
    fetch_trending_movies,
    fetch_recent_movies
]

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.6
)

tools = [fetch_watched_movies, recommend_movies, summarize_movie_taste, fetch_trending_movies, fetch_recent_movies]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly Movie Agent, ready to talk all things cinema! I can chat with you about movies, genres, actors, or anything else related to films. If you want me to analyze your movie taste or provide recommendations, please explicitly ask me to do so. For example, you can say \"Recommend some movies for me\" or \"What kind of movies do I like?\"\n\nHere's how I can help with recommendations and taste analysis:\n\n- If the user asks for movie recommendations or taste analysis, first use the `fetch_watched_movies` tool to get their watched history from Emby. Then, use the `recommend_movies` tool to get taste-based recommendations from Qloo based on the watched history and user location. Finally, use the `summarize_movie_taste` tool to summarize how well the recommendations match the user's taste.\n- If the user asks for trending movies, use the `fetch_trending_movies` tool.\n- If the user asks for recent movies, use the `fetch_recent_movies` tool.\n\nOtherwise, engage in general conversation about movies."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    # First, fetch watched movies to find the most common genre
    watched_movies = fetch_watched_movies.invoke({})
    if watched_movies:
        all_genres = [genre for m in watched_movies for genre in m.get('Genres', [])]
        if all_genres:
            most_common_genre = max(set(all_genres), key=all_genres.count)
        else:
            most_common_genre = 'comedy'  # Default genre
    else:
        most_common_genre = 'comedy'  # Default genre

    question = f"What kind of movies do I like based on my Emby history, and are the Qloo recommendations for '{most_common_genre}' a good fit?"
    result = agent_executor.invoke({"input": question})
    print("\n🎯 Agent Response:\n", result["output"])
