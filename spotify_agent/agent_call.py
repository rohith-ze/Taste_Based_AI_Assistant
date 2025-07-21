
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from data_gathering import get_playlist, get_last_played, get_song_list, get_liked_songs
from qloo_call import get_qloo_recommendations
from langchain.memory import ConversationBufferMemory


# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is available
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash-lite",
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
    get_qloo_recommendations
]

# Updated system prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a music recommendation assistant that:

1. Fetches the user's Spotify data (recent plays, liked songs, playlists).
2. Gets music recommendations from Qloo using the `get_qloo_recommendations` tool:
   - Extracts artist names from the tracks.
   - Fetches recommendations based on the artists.

Your goals:
- Use appropriate tools based on user queries
- Be concise and helpful
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])




# New system prompt focusing on visualization




# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools,memory=memory, verbose=True)

if __name__ == "__main__":
    # Example usage of the agent
    query = "Get music recommendations based on my recently played songs."
    response = agent_executor.invoke({"input": query})
    print(response)
