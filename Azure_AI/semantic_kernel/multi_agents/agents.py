# Add references
# Add references
import asyncio
from semantic_kernel.agents import Agent, ChatCompletionAgent, SequentialOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent



def get_agents() -> list[Agent]:
    # Agent instructions
    summarizer_instructions="""
    Summarize the customer's feedback in one short sentence. Keep it neutral and concise.
    Example output:
    App crashes during photo upload.
    User praises dark mode feature.
    """

    classifier_instructions="""
    Classify the feedback as one of the following: Positive, Negative, or Feature request.
    """

    action_instructions="""
    Based on the summary and classification, suggest the next action in one short sentence.
    Example output:
    Escalate as a high-priority bug for the mobile team.
    Log as positive feedback to share with design and marketing.
    Log as enhancement request for product backlog.
    """
    # Create a summarizer agent
    summarizer_agent = ChatCompletionAgent(
       name="SummarizerAgent",
       instructions=summarizer_instructions,
       service=AzureChatCompletion(),
    )

    # Create a classifier agent
    classifier_agent = ChatCompletionAgent(
       name="ClassifierAgent",
        instructions=classifier_instructions,
       service=AzureChatCompletion(),
    )

    # create an action agent
    action_agent = ChatCompletionAgent(
       name="ActionAgent",
       instructions=action_instructions,
       service=AzureChatCompletion(),
    )
    return [summarizer_agent, classifier_agent, action_agent]


def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"# {message.name}\n{message.content}")


async def main():
    # Initialize the input task
    task="""
    I tried updating my profile picture several times today, but the app kept freezing halfway through the process. 
    I had to restart it three times, and in the end, the picture still wouldn't upload. 
    It's really frustrating and makes the app feel unreliable.
    """

    # Create a sequential orchestration with a response callback to observe the output from each agent.
    sequential_orchestration = SequentialOrchestration(
       members=get_agents(),
       agent_response_callback=agent_response_callback,
    )

    # Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()
    # Invoke the orchestration with a task and the runtime
    orchestration_result = await sequential_orchestration.invoke(
       task=task,
       runtime=runtime,
    )

    # Wait for the results
    value = await orchestration_result.get(timeout=20)
    print(f"\n****** Task Input ******{task}")
    print(f"***** Final Result *****\n{value}")    

    # Stop the runtime when idle
    await runtime.stop_when_idle()    

if __name__ == "__main__":
    asyncio.run(main())
    