class TestUserStory5ConversationFlows:
    """
    Test User Story 5: Delete Tasks via Natural Language.

    Covers 5 acceptance scenarios from spec.md:
    1. Delete specific task by ID (Delete task 3)
    2. Delete task by description (Delete the meeting task)
    3. Error when task doesn't exist (Delete non-existent task)
    4. User isolation (can't delete other user's tasks)
    5. Confirmation of deletion (verify task is gone)

    Task: T077 - Write conversation flow tests for US5
    """

    @pytest.mark.asyncio
    async def test_delete_specific_task_by_id(self, test_db, test_user, test_client, mock_auth):
        """Scenario 1: Delete specific task by ID (Delete task 3)."""
        app.dependency_overrides[get_current_user] = mock_auth

        try:
            # Create a task to delete
            task = Task(
                user_id=test_user.id,
                title="Meeting preparation",
                is_complete=False,
            )
            test_db.add(task)
            await test_db.commit()
            await test_db.refresh(task)

            with patch("app.api.chat.get_agent") as mock_get_agent:
                mock_agent = AsyncMock()
                mock_agent.process_message = AsyncMock(
                    return_value={
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_delete_task",
                                "type": "function",
                                "function": {
                                    "name": "delete_task",
                                    "arguments": f'{{"user_id": "{test_user.id}", "task_id": {task.id}}}',
                                },
                            }
                        ],
                        "finish_reason": "tool_calls",
                    }
                )

                mock_agent.execute_tool_calls = AsyncMock(
                    return_value=[
                        {
                            "role": "tool",
                            "tool_call_id": "call_delete_task",
                            "content": f'{{"status": "deleted", "task_id": {task.id}, "title": "Meeting preparation", "message": "Task \'Meeting preparation\' has been deleted successfully"}}',
                        }
                    ]
                )

                mock_agent.client = AsyncMock()
                mock_agent.client.chat.completions.create = AsyncMock(
                    return_value=AsyncMock(
                        choices=[
                            AsyncMock(
                                message=AsyncMock(
                                    content=f"Task {task.id} ('Meeting preparation') has been deleted successfully."
                                )
                            )
                        ]
                    )
                )
                mock_agent.model = "gpt-4-turbo-preview"
                mock_agent.system_prompt = "You are a helpful assistant"
                mock_agent.mcp_tools = {"delete_task": AsyncMock()}
                mock_get_agent.return_value = mock_agent

                response = await test_client.post(
                    f"/api/chat/{test_user.id}",
                    json={"message": f"Delete task {task.id}"},
                    headers={"Authorization": "Bearer test_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
            assert str(task.id) in data["message"]
            assert "meeting preparation" in data["message"].lower()
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    @pytest.mark.asyncio
    async def test_delete_task_by_description(self, test_db, test_user, test_client, mock_auth):
        """Scenario 2: Delete task by description (Delete the meeting task)."""
        app.dependency_overrides[get_current_user] = mock_auth

        try:
            # Create a task to delete
            task = Task(
                user_id=test_user.id,
                title="Grocery shopping",
                description="Buy milk, eggs, and bread",
                is_complete=False,
            )
            test_db.add(task)
            await test_db.commit()
            await test_db.refresh(task)

            with patch("app.api.chat.get_agent") as mock_get_agent:
                mock_agent = AsyncMock()
                mock_agent.process_message = AsyncMock(
                    return_value={
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_delete_by_desc",
                                "type": "function",
                                "function": {
                                    "name": "delete_task",
                                    "arguments": f'{{"user_id": "{test_user.id}", "task_id": {task.id}}}',
                                },
                            }
                        ],
                        "finish_reason": "tool_calls",
                    }
                )

                mock_agent.execute_tool_calls = AsyncMock(
                    return_value=[
                        {
                            "role": "tool",
                            "tool_call_id": "call_delete_by_desc",
                            "content": f'{{"status": "deleted", "task_id": {task.id}, "title": "Grocery shopping", "message": "Task \'Grocery shopping\' has been deleted successfully"}}',
                        }
                    ]
                )

                mock_agent.client = AsyncMock()
                mock_agent.client.chat.completions.create = AsyncMock(
                    return_value=AsyncMock(
                        choices=[
                            AsyncMock(
                                message=AsyncMock(
                                    content="The grocery shopping task has been deleted successfully."
                                )
                            )
                        ]
                    )
                )
                mock_agent.model = "gpt-4-turbo-preview"
                mock_agent.system_prompt = "You are a helpful assistant"
                mock_agent.mcp_tools = {"delete_task": AsyncMock()}
                mock_get_agent.return_value = mock_agent

                response = await test_client.post(
                    f"/api/chat/{test_user.id}",
                    json={"message": "Delete the grocery shopping task"},
                    headers={"Authorization": "Bearer test_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
            assert "grocery shopping" in data["message"].lower()
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    @pytest.mark.asyncio
    async def test_error_task_does_not_exist(self, test_db, test_user, test_client, mock_auth):
        """Scenario 3: Error when task doesn't exist (Delete non-existent task)."""
        app.dependency_overrides[get_current_user] = mock_auth

        try:
            with patch("app.api.chat.get_agent") as mock_get_agent:
                mock_agent = AsyncMock()
                mock_agent.process_message = AsyncMock(
                    return_value={
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_delete_error",
                                "type": "function",
                                "function": {
                                    "name": "delete_task",
                                    "arguments": f'{{"user_id": "{test_user.id}", "task_id": 999}}',
                                },
                            }
                        ],
                        "finish_reason": "tool_calls",
                    }
                )

                mock_agent.execute_tool_calls = AsyncMock(
                    return_value=[
                        {
                            "role": "tool",
                            "tool_call_id": "call_delete_error",
                            "content": '{"status": "error", "task_id": 999, "title": "", "message": "Task with ID 999 not found or doesn\'t belong to user"}',
                        }
                    ]
                )

                mock_agent.client = AsyncMock()
                mock_agent.client.chat.completions.create = AsyncMock(
                    return_value=AsyncMock(
                        choices=[
                            AsyncMock(
                                message=AsyncMock(
                                    content="I couldn't find task 999. Would you like to see your task list?"
                                )
                            )
                        ]
                    )
                )
                mock_agent.model = "gpt-4-turbo-preview"
                mock_agent.system_prompt = "You are a helpful assistant"
                mock_agent.mcp_tools = {"delete_task": AsyncMock()}
                mock_get_agent.return_value = mock_agent

                response = await test_client.post(
                    f"/api/chat/{test_user.id}",
                    json={"message": "Delete task 999"},
                    headers={"Authorization": "Bearer test_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "couldn't find" in data["message"].lower() or "not found" in data["message"].lower()
            assert "999" in data["message"]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    @pytest.mark.asyncio
    async def test_user_isolation_cannot_delete_other_users_task(self, test_db, test_user, test_client, mock_auth):
        """Scenario 4: User isolation (can't delete other user's tasks)."""
        app.dependency_overrides[get_current_user] = mock_auth

        try:
            # Create a task for a different user
            other_user_task = Task(
                user_id="other_user_id",
                title="Other user's task",
                is_complete=False,
            )
            test_db.add(other_user_task)
            await test_db.commit()
            await test_db.refresh(other_user_task)

            with patch("app.api.chat.get_agent") as mock_get_agent:
                mock_agent = AsyncMock()
                mock_agent.process_message = AsyncMock(
                    return_value={
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_delete_isolation",
                                "type": "function",
                                "function": {
                                    "name": "delete_task",
                                    "arguments": f'{{"user_id": "{test_user.id}", "task_id": {other_user_task.id}}}',
                                },
                            }
                        ],
                        "finish_reason": "tool_calls",
                    }
                )

                mock_agent.execute_tool_calls = AsyncMock(
                    return_value=[
                        {
                            "role": "tool",
                            "tool_call_id": "call_delete_isolation",
                            "content": f'{{"status": "error", "task_id": {other_user_task.id}, "title": "", "message": "Task with ID {other_user_task.id} not found or doesn\'t belong to user"}}',
                        }
                    ]
                )

                mock_agent.client = AsyncMock()
                mock_agent.client.chat.completions.create = AsyncMock(
                    return_value=AsyncMock(
                        choices=[
                            AsyncMock(
                                message=AsyncMock(
                                    content=f"I couldn't find task {other_user_task.id}. It might belong to another user or may not exist."
                                )
                            )
                        ]
                    )
                )
                mock_agent.model = "gpt-4-turbo-preview"
                mock_agent.system_prompt = "You are a helpful assistant"
                mock_agent.mcp_tools = {"delete_task": AsyncMock()}
                mock_get_agent.return_value = mock_agent

                response = await test_client.post(
                    f"/api/chat/{test_user.id}",
                    json={"message": f"Delete task {other_user_task.id}"},
                    headers={"Authorization": "Bearer test_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "couldn't find" in data["message"].lower()
            assert str(other_user_task.id) in data["message"]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    @pytest.mark.asyncio
    async def test_confirmation_of_deletion_verify_task_gone(self, test_db, test_user, test_client, mock_auth):
        """Scenario 5: Confirmation of deletion (verify task is gone)."""
        app.dependency_overrides[get_current_user] = mock_auth

        try:
            # Create a task to delete
            task = Task(
                user_id=test_user.id,
                title="Task to delete",
                is_complete=False,
            )
            test_db.add(task)
            await test_db.commit()
            await test_db.refresh(task)

            # First, verify the task exists
            from app.models import Task as TaskModel
            existing_task = await test_db.get(TaskModel, task.id)
            assert existing_task is not None
            assert existing_task.title == "Task to delete"

            with patch("app.api.chat.get_agent") as mock_get_agent:
                mock_agent = AsyncMock()
                mock_agent.process_message = AsyncMock(
                    return_value={
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_confirm_deletion",
                                "type": "function",
                                "function": {
                                    "name": "delete_task",
                                    "arguments": f'{{"user_id": "{test_user.id}", "task_id": {task.id}}}',
                                },
                            }
                        ],
                        "finish_reason": "tool_calls",
                    }
                )

                mock_agent.execute_tool_calls = AsyncMock(
                    return_value=[
                        {
                            "role": "tool",
                            "tool_call_id": "call_confirm_deletion",
                            "content": f'{{"status": "deleted", "task_id": {task.id}, "title": "Task to delete", "message": "Task \'Task to delete\' has been deleted successfully"}}',
                        }
                    ]
                )

                mock_agent.client = AsyncMock()
                mock_agent.client.chat.completions.create = AsyncMock(
                    return_value=AsyncMock(
                        choices=[
                            AsyncMock(
                                message=AsyncMock(
                                    content=f"Task {task.id} ('Task to delete') has been deleted. It is no longer in your task list."
                                )
                            )
                        ]
                    )
                )
                mock_agent.model = "gpt-4-turbo-preview"
                mock_agent.system_prompt = "You are a helpful assistant"
                mock_agent.mcp_tools = {"delete_task": AsyncMock()}
                mock_get_agent.return_value = mock_agent

                response = await test_client.post(
                    f"/api/chat/{test_user.id}",
                    json={"message": f"Delete task {task.id}"},
                    headers={"Authorization": "Bearer test_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"].lower()
            assert "no longer in your task list" in data["message"].lower()

            # Verify the task is actually gone from the database after the deletion
            await test_db.refresh(existing_task)  # Refresh to check current state
            deleted_task = await test_db.get(TaskModel, task.id)
            assert deleted_task is None  # Task should be deleted
        finally:
            app.dependency_overrides.pop(get_current_user, None)