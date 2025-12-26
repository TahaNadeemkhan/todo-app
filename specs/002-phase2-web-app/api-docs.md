# API Documentation

Base URL: `/api`

## Authentication
Authentication is handled via JWT Bearer token in the `Authorization` header.
Token is issued by Better Auth (Frontend).

## Endpoints

### Tasks

#### List Tasks
`GET /api/{user_id}/tasks`
- Returns a list of tasks for the specified user.
- **Auth**: Required. `user_id` must match token subject.

#### Create Task
`POST /api/{user_id}/tasks`
- Creates a new task.
- **Body**: `{ "title": "string", "description": "string?" }`
- **Auth**: Required.

#### Get Task
`GET /api/{user_id}/tasks/{task_id}`
- Get details of a specific task.
- **Auth**: Required. Task must belong to user.

#### Update Task
`PUT /api/{user_id}/tasks/{task_id}`
- Update task details.
- **Body**: `{ "title": "string?", "description": "string?" }`
- **Auth**: Required.

#### Delete Task
`DELETE /api/{user_id}/tasks/{task_id}`
- Permanently remove a task.
- **Auth**: Required.

#### Toggle Complete
`PATCH /api/{user_id}/tasks/{task_id}/complete`
- Toggle completion status of a task.
- **Auth**: Required.

## Errors
- `401 Unauthorized`: Missing or invalid token.
- `403 Forbidden`: Accessing another user's data.
- `404 Not Found`: Resource not found.
- `422 Unprocessable Entity`: Validation error.
