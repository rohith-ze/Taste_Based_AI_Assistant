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

script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.6
)

tools = [fetch_watched_movies, recommend_movies, summarize_movie_taste, fetch_trending_movies, fetch_recent_movies]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly Movie Agent, ready to talk all things cinema! I can chat with you about movies, genres, actors, or anything else related to films. If you want me to analyze your movie taste or provide recommendations, please explicitly ask me to do so. For example, you can say \"Recommend some movies for me\" or \"What kind of movies do I like?\"\n\nHere's how I can help with recommendations and taste analysis:\n\n- If the user asks for movie recommendations or taste analysis, first use the `fetch_watched_movies` tool to get their watched history from Emby. Then, use the `recommend_movies` tool to get taste-based recommendations from Qloo. The recommendations will be a list of markdown-formatted strings with movie titles and image URLs. You MUST present these recommendations to the user exactly as they are returned from the tool, under the heading '**Recommended Movies:**'. Do not reformat or change the list. Finally, use the `summarize_movie_taste` tool to summarize how well the recommendations match the user's taste.\n- If the user specifies a genre (e.g., \"recommend comedy movies\") or a language (e.g., \"recommend french movies\"), use the `genre` or `language` arguments in the `recommend_movies` tool.\n- The language filter is robust and supports a wide variety of languages, including but not limited to English, French, Spanish, Hindi, and Tamil. When a user asks for movies in a specific language, pass the language name directly to the `language` argument in the `recommend_movies` tool.\n- Even if you cannot find genre information for the recommended movies, you should still present the list of movies to the user. Do not apologize for being unable to filter. Simply provide the list you were able to retrieve.\n- If the `recommend_movies` tool returns an empty list, it means no movies were found matching the user's request. In this case, you should inform the user that you couldn't find any movies matching their criteria and ask if they would like to try a different search.\n- If the user asks for trending movies, use the `fetch_trending_movies` tool. If it returns an empty list, inform the user that you couldn't find any trending movies.\n- If the user asks for recent movies, use the `fetch_recent_movies` tool.\n\nOtherwise, engage in general conversation about movies."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    # First, fetch watched movies to find the most common genre
    watched_movies = fetch_watched_movies.invoke({})
    if isinstance(watched_movies, dict) and 'error' in watched_movies:
        print(f"[ERROR] {watched_movies['error']}")
    else:
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
