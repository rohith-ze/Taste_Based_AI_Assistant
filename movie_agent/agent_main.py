# agent.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools import fetch_watched_movies, qloo_recommend_movies, gemini_taste_summary

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-pro",
    temperature=0.7,
    google_api_key=api_key
)

tools = [fetch_watched_movies, qloo_recommend_movies, gemini_taste_summary]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a movie taste assistant. Use Emby history to identify what the user likes. Recommend similar movies using qloo_recommend_movies tools definitions and do not use your own recommendations (from gemini) and explain their relevance using Gemini."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    query = "What kind of movies do I like based on my Emby history, and are the Qloo recommendations a good fit?"
    result = agent_executor.invoke({"input": query})
    print("\n🎯 Agent Response:\n", result)
