import os
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext, ModelMessage, ModelRequest, UserPromptPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from .deps import Deps
from .enums import AgentModes
from .tools import router_toolset, jobs_toolset

load_dotenv()


def create_model() -> OpenAIChatModel:
    return OpenAIChatModel(
        model_name="gpt-5.2",
        provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
        settings=ModelSettings(
            max_tokens=1000,
        )
    )
    
    
def get_system_prompt() -> str:
    return (
        "You are a helpful assistant that provides information to users based on their requests. "
        "You can only help the user via tool calls and responding with information. "
        "All information must come from the tools you use and the context available to you. "
        "Do not invent information or tools."
    )
    
    
def dynamic_context_wrapper(func):
    def wrapper(ctx: RunContext[Deps]) -> str:
        prefix = "<system_message>\n"
        event_str = (
            "Your recent actions:\n" 
            + ("\n".join(ctx.deps.event_history) if ctx.deps.event_history else "No recent actions.")
        )
        suffix = "\n</system_message>"
        return prefix + func(ctx) + "\n\n" + event_str + suffix
    return wrapper
    
    
@dynamic_context_wrapper
def job_dynamic_context(ctx: RunContext[Deps]) -> str:
    current_jobs_dict = {
        job.id: job.name for job in ctx.deps.jobs
    }
    if not current_jobs_dict:
        return "There are currently no jobs."
    return "Current jobs:\n" + "\n".join([f"{id}: {name}" for id, name in current_jobs_dict.items()])


def _is_model_request_with_user_prompt(message: ModelMessage) -> bool:
    if isinstance(message, ModelRequest) and isinstance(message.parts[-1], UserPromptPart):
        return True
    return False


def context_processor(
    ctx: RunContext[Deps],
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    # get last message in messages that is of type ModelRequest
    last_message = next((m for m in reversed(messages) if _is_model_request_with_user_prompt(m)), None)
    if not last_message:
        raise ValueError("No ModelRequest found in message history")
    last_part = last_message.parts[-1]
    match ctx.deps.agent_mode.value:
        case AgentModes.ROUTER.value:
            pass # No additional context needed
        case AgentModes.JOBS.value:
            last_part.content = job_dynamic_context(ctx) + "\n\n" + last_part.content
        case AgentModes.APPROVALS.value:
            pass # TODO
        case AgentModes.ESTIMATIONS.value:
            pass # TODO
        case _:
            raise ValueError("Invalid agent mode: " + ctx.deps.agent_mode.value)
    return messages


def create_agent() -> Agent[Deps]:
    agent = Agent(
        model=create_model(),
        system_prompt=get_system_prompt(),
        deps_type=Deps,
        name="Agent",
        history_processors=[
            context_processor
        ],
        retries=5,
        toolsets=[
            router_toolset,
            jobs_toolset
        ],
    )
    return agent