import asyncio
from langchain_groq import ChatGroq

from mcp_use import MCPAgent, MCPClient
import os
from dotenv import load_dotenv

async def run_memory_chat():
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API")

    # config file path
    config_file = "server/weather.json"

    print("Initiating chat...")

    # Create MCP client and agent with memory
    client = MCPClient.from_config_file(config_file)
    llm = ChatGroq(model="llama-3.1-8b-instant")

    # create agent with memory enabled = true
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True
    )

    print("\n*******Interactive MCP Chat*****************")
    print("Type quit to exit the conversation")
    print("===========================================")

    try:

        while True:

            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation")
                break

            if user_input.lower == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared")
                continue

            print("\nAssistant: ", end="", flush=True)

            try:
                #run agent with user input
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        if client and client.sessions:
            await client.close_all_sessions()

if __name__== "__main__":
    asyncio.run(run_memory_chat()) 


