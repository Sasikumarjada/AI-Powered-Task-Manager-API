import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch
import json

from main import app
from app.database import Base, get_db
from app.services import AIService

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_ai_service():
    """Override AI service dependency for testing"""
    service = AIService()
    service.analyze_task = AsyncMock(return_value={
        "summary": "Test task summary",
        "suggested_priority": "high"
    })
    return service


# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[AIService] = override_ai_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestTaskCreation:
    """Test POST /tasks endpoint"""
    
    def test_create_task_success(self):
        """Test successful task creation with AI analysis"""
        response = client.post(
            "/tasks",
            json={
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation for the API project including setup instructions and examples",
                "status": "todo"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete project documentation"
        assert data["status"] == "todo"
        assert data["ai_summary"] == "Test task summary"
        assert data["ai_suggested_priority"] == "high"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_task_with_explicit_priority(self):
        """Test task creation with user-specified priority"""
        response = client.post(
            "/tasks",
            json={
                "title": "Review code",
                "description": "Review the latest pull request",
                "priority": "low"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "low"
    
    def test_create_task_invalid_status(self):
        """Test task creation with invalid status"""
        response = client.post(
            "/tasks",
            json={
                "title": "Test task",
                "description": "Test description",
                "status": "invalid_status"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_task_missing_title(self):
        """Test task creation without title"""
        response = client.post(
            "/tasks",
            json={
                "description": "Test description"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_task_empty_title(self):
        """Test task creation with empty title"""
        response = client.post(
            "/tasks",
            json={
                "title": "   ",
                "description": "Test description"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_task_title_too_long(self):
        """Test task creation with title exceeding max length"""
        response = client.post(
            "/tasks",
            json={
                "title": "a" * 201,
                "description": "Test description"
            }
        )
        
        assert response.status_code == 422


class TestTaskRetrieval:
    """Test GET /tasks endpoints"""
    
    def test_get_all_tasks_empty(self):
        """Test retrieving tasks when none exist"""
        response = client.get("/tasks")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks"""
        # Create test tasks
        client.post("/tasks", json={
            "title": "Task 1",
            "description": "Description 1",
            "status": "todo"
        })
        client.post("/tasks", json={
            "title": "Task 2",
            "description": "Description 2",
            "status": "in_progress"
        })
        
        response = client.get("/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_tasks_with_status_filter(self):
        """Test filtering tasks by status"""
        client.post("/tasks", json={
            "title": "Task 1",
            "description": "Description 1",
            "status": "todo"
        })
        client.post("/tasks", json={
            "title": "Task 2",
            "description": "Description 2",
            "status": "done"
        })
        
        response = client.get("/tasks?status_filter=todo")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "todo"
    
    def test_get_tasks_with_priority_filter(self):
        """Test filtering tasks by priority"""
        client.post("/tasks", json={
            "title": "Task 1",
            "description": "Description 1",
            "priority": "high"
        })
        client.post("/tasks", json={
            "title": "Task 2",
            "description": "Description 2",
            "priority": "low"
        })
        
        response = client.get("/tasks?priority_filter=high")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"
    
    def test_get_task_by_id(self):
        """Test retrieving a specific task"""
        create_response = client.post("/tasks", json={
            "title": "Test Task",
            "description": "Test Description"
        })
        task_id = create_response.json()["id"]
        
        response = client.get(f"/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
    
    def test_get_nonexistent_task(self):
        """Test retrieving a task that doesn't exist"""
        response = client.get("/tasks/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestTaskUpdate:
    """Test PUT /tasks/{task_id} endpoint"""
    
    def test_update_task_success(self):
        """Test successful task update"""
        # Create task
        create_response = client.post("/tasks", json={
            "title": "Original Title",
            "description": "Original Description",
            "status": "todo"
        })
        task_id = create_response.json()["id"]
        
        # Update task
        response = client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Updated Title",
                "status": "in_progress"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["description"] == "Original Description"  # Unchanged
    
    def test_update_task_partial(self):
        """Test partial task update"""
        create_response = client.post("/tasks", json={
            "title": "Test Task",
            "description": "Test Description"
        })
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"priority": "high"}
        )
        
        assert response.status_code == 200
        assert response.json()["priority"] == "high"
    
    def test_update_nonexistent_task(self):
        """Test updating a task that doesn't exist"""
        response = client.put(
            "/tasks/999",
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 404
    
    def test_update_task_invalid_data(self):
        """Test updating task with invalid data"""
        create_response = client.post("/tasks", json={
            "title": "Test Task",
            "description": "Test Description"
        })
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"status": "invalid_status"}
        )
        
        assert response.status_code == 422


class TestTaskDeletion:
    """Test DELETE /tasks/{task_id} endpoint"""
    
    def test_delete_task_success(self):
        """Test successful task deletion"""
        create_response = client.post("/tasks", json={
            "title": "Task to Delete",
            "description": "This will be deleted"
        })
        task_id = create_response.json()["id"]
        
        response = client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist"""
        response = client.delete("/tasks/999")
        
        assert response.status_code == 404


class TestAIServiceIntegration:
    """Test AI service integration with mocking"""
    
    @patch('app.services.httpx.AsyncClient')
    async def test_ai_service_success(self, mock_client):
        """Test successful AI API call"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "content": [{
                "text": '{"summary": "AI generated summary", "suggested_priority": "high"}'
            }]
        }
        mock_response.raise_for_status = AsyncMock()
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        service = AIService()
        service.api_key = "test_key"
        
        result = await service.analyze_task("Test", "Test description")
        
        assert result["summary"] == "AI generated summary"
        assert result["suggested_priority"] == "high"
    
    @patch('app.services.httpx.AsyncClient')
    async def test_ai_service_timeout(self, mock_client):
        """Test AI service timeout handling"""
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
        
        service = AIService()
        service.api_key = "test_key"
        service.max_retries = 0
        
        with pytest.raises(Exception):
            await service.analyze_task("Test", "Test description")


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
