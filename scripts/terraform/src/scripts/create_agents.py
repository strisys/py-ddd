import argparse
import asyncio
from tabulate import tabulate

# https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects
from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential, AzureCliCredential, ChainedTokenCredential

from default_agent import create_default_agent

def parse_args():
    arg_configs = {
        "account-name": {
            "required": True,
            "help": "Azure AI Foundry account name",
            "display_name": "Account Name"
        },
        "project-name": {
            "required": True,
            "help": "Azure AI Foundry project name",
            "display_name": "Project Name"
        },
        "default-deployment": {
            "required": True,
            "help": "Azure AI Foundry default deployment name",
            "display_name": "Default Deployment"
        },
        "default-embedding-deployment": {
            "required": True,
            "help": "Azure AI Foundry default embedding deployment name",
            "display_name": "Default Embedding Deployment"
        }
    }
    
    parser = argparse.ArgumentParser(description="Azure AI Foundry agent script")
    
    for arg_name, config in arg_configs.items():
        parser.add_argument(
            f"--{arg_name}",
            required=config["required"],
            help=config["help"]
        )
    
    args = parser.parse_args()

    print("\n--- Azure Context ---")
    
    table_data = []

    for arg_name, config in arg_configs.items():
        arg_value = getattr(args, arg_name.replace("-", "_"))
        table_data.append([config['display_name'], arg_value])
    
    print(tabulate(table_data, headers=['Parameter', 'Value'], tablefmt='grid'))
    print()

    return args


def create_project_client(args) -> AIProjectClient:
    credential = ChainedTokenCredential(AzureCliCredential())
    project_endpoint = f"https://{args.account_name}.services.ai.azure.com/api/projects/{args.project_name}"

    return AIProjectClient(
        endpoint=project_endpoint,
        credential=credential
    )

# async def try_find_agent(agent_name: str, project_client: AIProjectClient):
#     agents_list = []
#     async for agent in project_client.agents.list_agents():
#         if agent.name == agent_name:
#             agents_list.append(agent)

#     if len(agents_list) > 1:
#         raise Error(f"Found more than one agent ({len(agents_list)}) with the name '{agent_name}'")

#     return agents_list[0] if agents_list else None

# async def create_default_agent(args, project_client: AIProjectClient):
#     agent_name = "default-agent"
#     agent = await try_find_agent(agent_name=agent_name, project_client=project_client)

#     if agent:
#         print(f"Deleting existing agent '{agent_name}'...")
#         await project_client.agents.delete_agent(agent.id)

#     print(f"Creating agent '{agent_name}'...")

#     await project_client.agents.create_agent(
#         model=args.default_deployment,
#         name=agent_name,
#         instructions="You are a helpful assistant.  Get it done.",
#         tools=[]
#     )

#     print(f"Agent '{agent_name}' created successfully!")

async def run_async():
    args = parse_args()
    project_client = create_project_client(args)
    
    try:
        await create_default_agent(args, project_client)
    finally:
        await project_client.close()

def run():
    asyncio.run(run_async())

if __name__ == "__main__":
    run()