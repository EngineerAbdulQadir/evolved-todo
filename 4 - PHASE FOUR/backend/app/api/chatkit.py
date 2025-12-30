"""
ChatKit FastAPI Endpoint

Exposes ChatKit server for frontend integration.

Task: ChatKit Integration
Spec: specs/003-phase3-ai-chatbot/spec.md
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from app.chatkit_server import TodoChatKitServer
from app.chatkit_store import DatabaseStore
from app.middleware.auth import get_current_user, TokenPayload
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize ChatKit server with database store
_store = DatabaseStore()
_chatkit_server = TodoChatKitServer(_store)


@router.post("/chatkit/session")
async def chatkit_session(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Create a ChatKit session and return client secret.

    This endpoint is called by the frontend to initialize ChatKit.
    For a fully custom backend, we need to use ChatKit SDK's session creation.
    """
    try:
        body_json = await request.json()
        user_id = body_json.get("user_id", current_user.sub)
        conversation_id = body_json.get("conversation_id")

        logger.info(f"Creating ChatKit session for user: {user_id}, conversation: {conversation_id}")

        # Create session using ChatKit server
        # For custom backends, we return our backend URL as the session endpoint
        session_data = {
            "backend_url": str(request.url_for("chatkit_endpoint")).replace("/session", ""),
            "user_id": user_id,
        }

        if conversation_id:
            session_data["conversation_id"] = conversation_id

        logger.info(f"Session data: {session_data}")

        return session_data

    except Exception as e:
        logger.error(f"ChatKit session error: {e}", exc_info=True)
        return {"error": str(e)}, 500


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    ChatKit endpoint that streams responses from the TodoChatKitServer.

    This endpoint receives ChatKit requests from the frontend and
    forwards them to our custom ChatKit server implementation.
    """
    try:
        # Get raw request body
        body = await request.body()

        logger.info(f"ChatKit request from user: {current_user.sub}")

        # Process request with ChatKit server
        # Pass user_id as context for authentication
        result = await _chatkit_server.process(body, context=current_user.sub)

        # Debug: Log response type and first chunk
        logger.info(f"ChatKit response type: {type(result).__name__}, is async iterable: {hasattr(result, '__aiter__')}")

        # Return streaming response
        if hasattr(result, '__aiter__'):
            # Streaming response
            async def event_generator():
                async for chunk in result:
                    yield chunk

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming response
            logger.info(f"ChatKit non-streaming response type: {type(result)}")

            # NonStreamingResult has a 'json' attribute with the actual response
            if hasattr(result, 'json'):
                json_response = result.json
                logger.info(f"Response JSON type: {type(json_response)}")
                logger.info(f"Response JSON (first 500 chars): {json_response[:500] if isinstance(json_response, bytes) else str(json_response)[:500]}")

                # Return JSONResponse with proper headers
                from fastapi.responses import Response
                return Response(
                    content=json_response,
                    media_type="application/json",
                    headers={
                        "Cache-Control": "no-cache",
                    }
                )
            else:
                return result

    except Exception as e:
        logger.error(f"ChatKit endpoint error: {e}", exc_info=True)
        return {"error": str(e)}, 500
