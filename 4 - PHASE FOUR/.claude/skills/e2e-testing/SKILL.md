---
name: e2e-testing
description: End-to-end testing strategies across frontend and backend, user journey validation, and integration testing.
---

# End-to-End Testing

## Instructions

### When to Use

- Testing complete user journeys across frontend and backend
- Validating frontend-backend integration
- Testing authentication flows
- Verifying API contracts end-to-end
- Testing critical user workflows
- Ensuring cross-stack functionality

## Testing Strategy

### Testing Pyramid

```
           /\
          /E2E\        Few, slow, expensive
         /------\
        /Integration\   Some, moderate speed
       /------------\
      /  Unit Tests  \  Many, fast, cheap
     /----------------\
```

**E2E Tests:**
- Test complete user flows
- Test across frontend + backend
- Test authentication and authorization
- Test critical business paths
- Run before deployment

## Backend E2E Testing (pytest + httpx)

### Test Setup

```python
# tests/conftest.py
import pytest
import asyncio
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from httpx import AsyncClient

from app.main import app
from app.database import get_session

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def session(engine):
    """Create test database session."""
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(session):
    """Create test client with overridden dependencies."""
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
async def auth_user(session):
    """Create authenticated test user."""
    from app.models.user import User
    from app.auth.jwt import create_access_token

    # Create user
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create auth token
    token = create_access_token(user.id, user.email)

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
```

### E2E Test Examples

```python
# tests/e2e/test_task_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_task_lifecycle(client: AsyncClient, auth_user):
    """
    Test complete task lifecycle: create -> read -> update -> delete.

    This tests the full user journey for managing a task.
    """
    user_id = auth_user["user"].id
    headers = auth_user["headers"]

    # Step 1: Create task
    create_response = await client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Test task",
            "description": "Test description",
            "priority": "high"
        },
        headers=headers
    )

    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]
    assert task["title"] == "Test task"
    assert task["priority"] == "high"
    assert task["completed"] is False

    # Step 2: Read task
    read_response = await client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers=headers
    )

    assert read_response.status_code == 200
    assert read_response.json()["id"] == task_id

    # Step 3: Update task
    update_response = await client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={
            "title": "Updated task",
            "completed": True
        },
        headers=headers
    )

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated task"
    assert updated_task["completed"] is True

    # Step 4: Delete task
    delete_response = await client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers=headers
    )

    assert delete_response.status_code == 204

    # Step 5: Verify task is deleted
    get_response = await client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers=headers
    )

    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_authentication_flow(client: AsyncClient):
    """
    Test complete authentication flow: register -> login -> access protected route.
    """
    # Step 1: Register user
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )

    assert register_response.status_code == 201
    user = register_response.json()
    user_id = user["id"]

    # Step 2: Login
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )

    assert login_response.status_code == 200
    auth_data = login_response.json()
    token = auth_data["access_token"]

    # Step 3: Access protected route with token
    protected_response = await client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert protected_response.status_code == 200

    # Step 4: Verify unauthenticated access fails
    unauth_response = await client.get(f"/api/{user_id}/tasks")
    assert unauth_response.status_code == 401

@pytest.mark.asyncio
async def test_user_isolation(client: AsyncClient, auth_user):
    """
    Test that users cannot access each other's tasks.
    """
    user1_id = auth_user["user"].id
    user1_headers = auth_user["headers"]

    # Create task for user 1
    task_response = await client.post(
        f"/api/{user1_id}/tasks",
        json={"title": "User 1 task"},
        headers=user1_headers
    )
    task_id = task_response.json()["id"]

    # Create second user
    user2_response = await client.post(
        "/api/auth/register",
        json={
            "email": "user2@example.com",
            "password": "password"
        }
    )
    user2_id = user2_response.json()["id"]
    user2_token = user2_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to access User 1's task
    forbidden_response = await client.get(
        f"/api/{user1_id}/tasks/{task_id}",
        headers=user2_headers
    )

    assert forbidden_response.status_code == 403
```

## Frontend E2E Testing (Playwright)

### Playwright Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E Test Examples

```typescript
// e2e/task-management.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('complete task lifecycle', async ({ page }) => {
    // Navigate to tasks page
    await page.goto('/tasks')

    // Create new task
    await page.click('button:has-text("New Task")')
    await page.fill('input[name="title"]', 'E2E Test Task')
    await page.fill('textarea[name="description"]', 'Created by E2E test')
    await page.selectOption('select[name="priority"]', 'high')
    await page.click('button:has-text("Create")')

    // Verify task appears in list
    await expect(page.locator('text=E2E Test Task')).toBeVisible()

    // Edit task
    await page.click('button[aria-label="Edit task"]')
    await page.fill('input[name="title"]', 'Updated E2E Task')
    await page.click('button:has-text("Save")')

    // Verify update
    await expect(page.locator('text=Updated E2E Task')).toBeVisible()

    // Mark as complete
    await page.click('input[type="checkbox"]')
    await expect(page.locator('text=Updated E2E Task')).toHaveClass(/completed/)

    // Delete task
    await page.click('button[aria-label="Delete task"]')
    await page.click('button:has-text("Confirm")')

    // Verify deletion
    await expect(page.locator('text=Updated E2E Task')).not.toBeVisible()
  })

  test('task filtering', async ({ page }) => {
    await page.goto('/tasks')

    // Apply completed filter
    await page.selectOption('select[name="filter"]', 'completed')
    await expect(page.locator('[data-testid="task-item"]')).toHaveCount(0)

    // Apply active filter
    await page.selectOption('select[name="filter"]', 'active')
    const activeTasks = await page.locator('[data-testid="task-item"]').count()
    expect(activeTasks).toBeGreaterThan(0)

    // Apply priority filter
    await page.selectOption('select[name="priority-filter"]', 'high')
    const highPriorityTasks = await page.locator('[data-priority="high"]').count()
    expect(highPriorityTasks).toBeGreaterThan(0)
  })

  test('task search', async ({ page }) => {
    await page.goto('/tasks')

    // Search for tasks
    await page.fill('input[type="search"]', 'important')
    await expect(page.locator('text=important')).toBeVisible()

    // Clear search
    await page.fill('input[type="search"]', '')
    const allTasks = await page.locator('[data-testid="task-item"]').count()
    expect(allTasks).toBeGreaterThan(0)
  })
})

test.describe('Authentication', () => {
  test('successful login flow', async ({ page }) => {
    await page.goto('/login')

    // Fill login form
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('failed login with invalid credentials', async ({ page }) => {
    await page.goto('/login')

    // Fill with invalid credentials
    await page.fill('input[name="email"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // Verify error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible()
    await expect(page).toHaveURL('/login')
  })

  test('protected route redirects to login', async ({ page }) => {
    // Try to access protected route without authentication
    await page.goto('/dashboard')

    // Verify redirect to login
    await expect(page).toHaveURL('/login')
  })
})
```

## Full-Stack E2E Testing

### Complete User Journey

```typescript
// e2e/full-stack.spec.ts
import { test, expect } from '@playwright/test'
import { createTestUser, cleanupTestUser } from './helpers'

test.describe('Full-Stack Integration', () => {
  let testUser: { email: string; password: string }

  test.beforeAll(async () => {
    // Create test user in backend
    testUser = await createTestUser()
  })

  test.afterAll(async () => {
    // Cleanup test data
    await cleanupTestUser(testUser.email)
  })

  test('complete user journey: register -> login -> create task -> logout', async ({ page }) => {
    // Step 1: Navigate to registration
    await page.goto('/register')
    await page.fill('input[name="email"]', testUser.email)
    await page.fill('input[name="password"]', testUser.password)
    await page.click('button[type="submit"]')

    // Step 2: Verify successful registration and auto-login
    await expect(page).toHaveURL('/dashboard')

    // Step 3: Create a task
    await page.goto('/tasks')
    await page.click('button:has-text("New Task")')
    await page.fill('input[name="title"]', 'Integration Test Task')
    await page.click('button:has-text("Create")')

    // Step 4: Verify task creation
    await expect(page.locator('text=Integration Test Task')).toBeVisible()

    // Step 5: Verify backend has the task
    const response = await page.request.get(`http://localhost:8000/api/tasks`)
    const tasks = await response.json()
    expect(tasks.some((t: any) => t.title === 'Integration Test Task')).toBe(true)

    // Step 6: Logout
    await page.click('button[aria-label="User menu"]')
    await page.click('button:has-text("Logout")')

    // Step 7: Verify logout
    await expect(page).toHaveURL('/login')
  })
})
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-backend:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          cd backend
          pip install uv
          uv sync

      - name: Run E2E tests
        run: |
          cd backend
          uv run pytest tests/e2e/ -v

  e2e-frontend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          pnpm install
          pnpm playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd frontend
          pnpm test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Integration with fullstack-integrator Subagent

This skill is primarily used by:
- **fullstack-integrator** - For validating E2E integration
- **test-guardian** - For comprehensive test coverage

### Key Principles

1. **Test User Journeys** - Test complete workflows, not just API endpoints
2. **Frontend + Backend** - Test across the entire stack
3. **Authentication** - Always test auth flows
4. **User Isolation** - Test that users can't access each other's data
5. **CI/CD Integration** - Run E2E tests before deployment
6. **Test Data Cleanup** - Always clean up test data after tests
