from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, ACTION_CONFIRMATION_MESSAGE
import os

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
   # In backend/agent.py
    model = openai.realtime.RealtimeModel(
    model="gpt-3.5-turbo",  # Use a less expensive model
    instructions=INSTRUCTIONS,
    voice="shimmer",
    temperature=0.8,
    modalities=["audio", "text"]
)
    assistant_fnc = AssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()
    
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
            
        if assistant_fnc.has_user_profile():
            handle_query(msg)
        else:
            create_user_profile(msg)
        
    def create_user_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=f"The user needs to create a profile. Ask them for their name and device type (Android/iOS). Here is the user's message: {msg.content}"
            )
        )
        session.response.create()
        
    def handle_query(msg: llm.ChatMessage):
        # Check if we're in the middle of a multi-step action
        if assistant_fnc.has_pending_action():
            # Handle confirmation for pending action
            if "confirm" in msg.content.lower() or "yes" in msg.content.lower() or "approve" in msg.content.lower():
                session.conversation.item.create(
                    llm.ChatMessage(
                        role="system",
                        content=f"The user has approved the action. Execute it and provide confirmation. Action: {assistant_fnc.get_pending_action()}"
                    )
                )
                assistant_fnc.execute_pending_action()
            else:
                session.conversation.item.create(
                    llm.ChatMessage(
                        role="system",
                        content=f"The user has declined or provided additional information. Cancel the pending action and process the new request. User message: {msg.content}"
                    )
                )
                assistant_fnc.cancel_pending_action()
        else:
            # Process new request
            session.conversation.item.create(
                llm.ChatMessage(
                    role="user",
                    content=msg.content
                )
            )
            
        session.response.create()
    
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))