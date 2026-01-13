from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-3',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
