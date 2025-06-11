from azure.ai.projects.aio import AIProjectClient

async def try_find_agent(agent_name: str, project_client: AIProjectClient):
    agents_list = []
    
    async for agent in project_client.agents.list_agents():
        if agent.name == agent_name:
            agents_list.append(agent)

    if len(agents_list) > 1:
        raise ValueError(f"Found more than one agent ({len(agents_list)}) with the name '{agent_name}'")

    return agents_list[0] if agents_list else None