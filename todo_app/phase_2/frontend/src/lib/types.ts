/**
 * Shared TypeScript interfaces for the Todo App.
 */

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
}

export interface ApiError {
  detail: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}
