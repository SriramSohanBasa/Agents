##simple agent with langgraph and access tools.
##we get the tools from firecrawl- which has multiple mcp

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os


load_dotenv()

model = ChatOpenAI(
    model = "gpt-4.1",
    temperature = 0,
    openai_api_key = os.getenv("OPENAI_API_KEY")
)


##connecting to mcp server

server_params = StdioServerParameters(
    command = "npx",
    env = {
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),
    },
    args = ["firecrawl-mcp"]
)

async def main():
    async with stdio_client(server_params) as (read,write): ##read amnd write from client. calling a tool
        async with ClientSession(read,write) as session: #we are creating new session with client
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools) ## we got agent who has access to our openai models and tools

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can scrape websites and crawl pages, and extract data using Firecrawl tools. Think step by step and use appropriate tools to help the user."
                
                }

            ]

            print("Available Tools -", *[tool.name for tool in tools]) ##star used to unpack all tools
            print("-" * 50)

            while True:
                user_input = input("\nYou:")
                if user_input == "quit":
                    print("Goodbye")
                    break

                messages.append({"role": "user", "content": user_input[:175000]})

                #call agent
                try:
                    agent_response = await agent.ainvoke({"messages": messages})

                    ai_message = agent_response["messages"][-1].content ##need only l;ast message

                    print("\nAgent:" , ai_message)

                except Exception as e:
                    print("Error:",e)
                

if __name__ == "__main__":
    asyncio.run(main())