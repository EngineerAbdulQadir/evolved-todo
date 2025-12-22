"""Unit tests for SQLModel database models.

Tests for Phase 3 Conversation and Message models.

Task: T010 - Write model tests
Spec: specs/003-phase3-ai-chatbot/data-model.md
"""

from datetime import datetime

import pytest
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.models import Conversation, Message, MessageRole, SQLModel, User


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        id="user_123abc",
        email="test@example.com",
        name="Test User",
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class TestConversation:
    """Test cases for Conversation model."""

    def test_create_conversation(self, session: Session, test_user: User):
        """Test creating a conversation."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.id is not None
        assert conversation.user_id == test_user.id
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_timestamps(self, session: Session, test_user: User):
        """Test conversation timestamp handling."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        created_at = conversation.created_at
        updated_at = conversation.updated_at

        # Timestamps should be set
        assert created_at is not None
        assert updated_at is not None

        # created_at and updated_at should be similar at creation
        assert abs((updated_at - created_at).total_seconds()) < 1

    def test_conversation_user_relationship(self, session: Session, test_user: User):
        """Test conversation belongs to user."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.user_id == test_user.id

    def test_multiple_conversations_per_user(self, session: Session, test_user: User):
        """Test that a user can have multiple conversations."""
        conv1 = Conversation(user_id=test_user.id)
        conv2 = Conversation(user_id=test_user.id)
        session.add(conv1)
        session.add(conv2)
        session.commit()

        conversations = session.query(Conversation).filter(Conversation.user_id == test_user.id).all()
        assert len(conversations) == 2


class TestMessage:
    """Test cases for Message model."""

    def test_create_user_message(self, session: Session, test_user: User):
        """Test creating a user message."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        message = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Add a task to buy groceries",
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.user_id == test_user.id
        assert message.role == MessageRole.USER
        assert message.content == "Add a task to buy groceries"
        assert message.created_at is not None

    def test_create_assistant_message(self, session: Session, test_user: User):
        """Test creating an assistant message."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        message = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="I've added 'Buy groceries' to your task list. Task ID is 1.",
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        assert message.role == MessageRole.ASSISTANT
        assert message.content.startswith("I've added")

    def test_message_role_enum(self, session: Session, test_user: User):
        """Test message role enumeration."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        user_msg = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Test",
        )
        assistant_msg = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Test response",
        )

        session.add(user_msg)
        session.add(assistant_msg)
        session.commit()

        # Verify enum values are stored correctly
        assert user_msg.role == MessageRole.USER
        assert assistant_msg.role == MessageRole.ASSISTANT

    def test_message_content_length(self, session: Session, test_user: User):
        """Test message content length constraint."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Create message with long content (within limit)
        long_content = "A" * 5000  # Max allowed
        message = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content=long_content,
        )
        session.add(message)
        session.commit()

        assert len(message.content) == 5000

    def test_conversation_history_ordering(self, session: Session, test_user: User):
        """Test that messages can be ordered by created_at."""
        conversation = Conversation(user_id=test_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Create multiple messages
        msg1 = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="First message",
        )
        msg2 = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="First response",
        )
        msg3 = Message(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Second message",
        )

        session.add(msg1)
        session.commit()
        session.add(msg2)
        session.commit()
        session.add(msg3)
        session.commit()

        # Fetch messages ordered by created_at
        messages = (
            session.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
            .all()
        )

        assert len(messages) == 3
        assert messages[0].content == "First message"
        assert messages[1].content == "First response"
        assert messages[2].content == "Second message"

    def test_message_user_isolation(self, session: Session):
        """Test that messages are isolated by user_id."""
        # Create two users
        user1 = User(
            id="user_1",
            email="user1@example.com",
            name="User One",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        user2 = User(
            id="user_2",
            email="user2@example.com",
            name="User Two",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        # Create conversations for each user
        conv1 = Conversation(user_id=user1.id)
        conv2 = Conversation(user_id=user2.id)
        session.add(conv1)
        session.add(conv2)
        session.commit()
        session.refresh(conv1)
        session.refresh(conv2)

        # Create messages for each user
        msg1 = Message(
            conversation_id=conv1.id,
            user_id=user1.id,
            role=MessageRole.USER,
            content="User 1 message",
        )
        msg2 = Message(
            conversation_id=conv2.id,
            user_id=user2.id,
            role=MessageRole.USER,
            content="User 2 message",
        )
        session.add(msg1)
        session.add(msg2)
        session.commit()

        # Verify user 1 can only see their messages
        user1_messages = session.query(Message).filter(Message.user_id == user1.id).all()
        assert len(user1_messages) == 1
        assert user1_messages[0].content == "User 1 message"

        # Verify user 2 can only see their messages
        user2_messages = session.query(Message).filter(Message.user_id == user2.id).all()
        assert len(user2_messages) == 1
        assert user2_messages[0].content == "User 2 message"
