
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from data_gathering import get_playlist, get_last_played, get_song_list, get_liked_songs
from qloo_call import qloo_taste_analysis , generate_heatmap_from_tracks
from langchain.memory import ConversationBufferMemory
from heatmap import generate_map

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
    generate_heatmap_from_tracks,
    generate_map
]

# Updated system prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a music taste analyzer that:

1. Fetches the user's Spotify data (recent plays, liked songs, playlists).
2. Analyzes taste using Qloo via the `generate_heatmap_from_tracks` tool:
   - Automatically infers genres from tracks
   - Generates brand affinity and popularity values
3. Visualizes the results using `generate_map(latitude, longitude)`:
   - This tool **requires latitude and longitude values**
   - You **must always extract or infer the user's location** before calling it.
   - If the user gives a city or country, **convert it into latitude and longitude**

Your goals:
- Use appropriate tools based on user queries
- If the user wants a heatmap, **always pass lat and long to `generate_map`**
- Do not ask the user to provide lat/long — handle it yourself


RULES:
- Never modify genre tags — the tool handles this
- If heatmap data is insufficient, suggest trying more songs
- Be concise, visual, and helpful
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
    query = "Find my recently played songs, analyze my taste using Qloo, and summarize what kind of music I like. and  i am From India"
    response = agent_executor.invoke({"input": query})
    print(response)
    """
    query = "What was the last song I listened to?"
    response = agent_executor.invoke({"input": query})
    print(response)
    """
