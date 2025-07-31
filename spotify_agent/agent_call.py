import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from .data_gathering import get_playlist, get_last_played, get_song_list, get_liked_songs
from .qloo_call import get_artist_entity_id,get_insights
from langchain.memory import ConversationBufferMemory
import json

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")


# Check if the API key is available
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0.7,
    top_p=0.85,
    google_api_key=api_key
)

# Define the tools the agent can use
tools = [
    get_playlist,
    get_last_played, 
    get_song_list,
    get_liked_songs,
    get_artist_entity_id,
    get_insights

]

# Updated system prompt
# In agent_call.py
with open("/var/www/Taste_Based_AI_Assistant/spotify_agent/system_prompt.txt", "r") as f:
    system_prompt = f.read()

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])






# Create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create  agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools,memory=memory, verbose=True)

if __name__ == "__main__":
    query = "Get recommendations from my spotify account."
    response = agent_executor.invoke({"input": query})

