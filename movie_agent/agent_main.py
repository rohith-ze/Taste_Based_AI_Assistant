# agent_main.py
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from _movie_tools import fetch_watched_movies, recommend_movies, summarize_movie_taste, fetch_trending_movies, fetch_recent_movies
from langchain.memory import ConversationBufferMemory

tools = [
    fetch_watched_movies,
    recommend_movies,
    fetch_trending_movies,
    fetch_recent_movies
]

script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)
memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.6
)

tools = [fetch_watched_movies, 
        recommend_movies, 
        summarize_movie_taste,
        fetch_trending_movies,
        fetch_recent_movies
    ]

with open("/home/ajay/Documents/sleeping_dog_don/Taste_Based_AI_Assistant/movie_agent/system_prompt.txt", "r") as f:
    system_prompt = f.read()

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,memory=memory)

if __name__ == "__main__":
    question = "Recommend me some movies based on my watched history."
    result = agent_executor.invoke({"input": question})
    print("\n🎯 Agent Response:\n", result["output"])
