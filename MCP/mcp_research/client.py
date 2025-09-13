import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import re

import os
from dotenv import load_dotenv

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()
hf_key = os.getenv("HF_KEY")

repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

def hf_chatbot(prompt):
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        task="conversational",
        max_new_tokens=128,
        temperature=0.5,
        huggingfacehub_api_token=hf_key
    )

    chat_model = ChatHuggingFace(llm = llm)
    response = chat_model.invoke(prompt)
    return response.content

async def main():
            # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",  # Executable
        args=["run", "Server.py"],  # Optional command line arguments
    )
    async with stdio_client(server_params) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize()
            print("Connected to research mcp server.")
            print("Type your question")

            system_instructions = (
                "You are a research paper assistant. "
                "For queries about research papers, do not answer directly; instead, output calls to the search_paper or extract_info tool exactly as specified."
                "To search for papers, output search_paper(topic='...', max_results=...). "
                "To extract info, output extract_info(paper_id='...'). "
                "Only use one tool call per response. If you don't know, say so."
            )

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() == "quit":
                    print("Goodbye...")
                    break
                print("Answering your Query..")
                # Compose LLm prompt
                prompt = f"{system_instructions}\nUser: {user_input}\nAssistant:"

                # Get LLm output
                llm_response = hf_chatbot(prompt)
                print(f"\n[Chatbot]: {llm_response}")

                if "search_paper" in llm_response:
                    print("Inside search paper..")
                    m = re.search(r"search_paper\(topic=['\"](.+?)['\"],\s*max_results=(\d+)\)", llm_response)
                    if m:
                        topic = m.group(1)
                        max_results = int(m.group(2))
                        tool_result = await session.call_tool("search_paper", {"topic": topic, "max_results": max_results})
                        print("\n[Tool Result] Paper IDs:", tool_result.content or tool_result.structuredContent)

                elif 'extract_info' in llm_response:
                    print("inside extract info")
                    m = re.search(r"extract_info\(paper_id=['\"](.+?)['\"]\)", llm_response)
                    if m:
                        paper_id = m.group(1)
                        tool_result = await session.call_tool("extract_info", {"paper_id": paper_id})
                        print("\n[Tool Result] Paper Info:\n", tool_result.content or tool_result.structuredContent)

                else:
                    print("\n[No tool call detected. Conversation only or unhandled output.]")

if __name__ == "__main__":
    asyncio.run(main())