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
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Initialize Gemini 2 agent
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-pro",  # or "models/gemini-1.5-flash"
    temperature=0.7,
    google_api_key=api_key
)

# Tools the agent can call
tools = [fetch_watched_movies, qloo_recommend_movies, gemini_taste_summary]

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a movie taste assistant. Help users explore what kind of movies they like and what to watch next based on their Emby viewing history."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Executor to invoke agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    # Example query
    query = "Based on my recently watched movies, what kind of taste do I have? Also suggest 5 new movies I might enjoy."
    response = agent_executor.invoke({"input": query})
    print("\n🎯 Agent Response:\n", response)
