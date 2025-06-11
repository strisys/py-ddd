
from azure.ai.projects.aio import AIProjectClient
from shared import try_find_agent

async def create_default_agent(args, project_client: AIProjectClient):
    agent_name = "default-agent"
    agent = await try_find_agent(agent_name=agent_name, project_client=project_client)

    if agent:
        print(f"Deleting existing agent '{agent_name}'...")
        await project_client.agents.delete_agent(agent.id)

    print(f"Creating agent '{agent_name}'...")

    await project_client.agents.create_agent(
        model=args.default_deployment,
        name=agent_name,
        instructions="You are an extremely helpful assistant.",
        tools=[]
    )

    print(f"Agent '{agent_name}' created successfully!")