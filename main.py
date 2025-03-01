import asyncio
from rasa.core.agent import Agent
from rasa.utils.endpoints import EndpointConfig

async def process_message(agent, message_text, sender_id="default_user"):
    """Process a message using RASA agent and return responses."""
    responses = await agent.handle_text(message_text, sender_id=sender_id)
    return responses

async def load_agent():
    """Load a trained RASA agent."""
    # Path to your model directory
    model_path = "./models"
    
    # Endpoint for action server
    action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
    
    # Load the agent
    agent = Agent.load(model_path, action_endpoint=action_endpoint)
    return agent

# Example usage
async def main():
    agent = await load_agent()
    user_input = "I need to schedule an appointment with a cardiologist"
    
    responses = await process_message(agent, user_input)
    for response in responses:
        print(f"Bot: {response.get('text', '')}")

if __name__ == "__main__":
    asyncio.run(main())