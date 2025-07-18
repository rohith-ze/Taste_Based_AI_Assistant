# agent_main.py
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from movie_tools import fetch_watched_movies, recommend_movies, summarize_movie_taste

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.6
)

tools = [fetch_watched_movies, recommend_movies, summarize_movie_taste]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a movie taste analysis assistant. Use the tools to fetch watched movies from Emby, get taste-based recommendations from Qloo, and summarize how well the recommendations match the user's taste."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    question = "What kind of movies do I like based on my Emby history, and are the Qloo recommendations a good fit?"
    result = agent_executor.invoke({"input": question})
    print("\n🎯 Agent Response:\n", result["output"])
