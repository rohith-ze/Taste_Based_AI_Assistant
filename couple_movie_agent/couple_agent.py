from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from couple_tools import fetch_joint_watched_movies, recommend_couple_movies, summarize_couple_taste
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.6,
)

tools = [fetch_joint_watched_movies, recommend_couple_movies, summarize_couple_taste]

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a Couple Movie Recommendation Agent.
You can suggest movies for couples based on their shared watch history on Emby.

**Workflow Instructions:**
1. If the user asks for movie recommendations or couple taste analysis:
   - First call `fetch_joint_watched_movies` to get combined Emby history.
   - Then call `recommend_couple_movies` to fetch Qloo-based recommendations.
   - Finally, call `summarize_couple_taste` to explain why those movies match their preferences.

2. Do not ask the user for watched movies — fetch them automatically from Emby.
Always use the tools in the order above when asked for recommendations.

Present results under a heading:
**Recommended Movies:**
<list of markdown-formatted movie recommendations>

Engage naturally otherwise.
"""
    ),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    question = "Can you suggest some good movies for us to watch together?"
    result = agent_executor.invoke({"input": question})
    print("\n🎬 Couple Agent Response:\n", result["output"])
