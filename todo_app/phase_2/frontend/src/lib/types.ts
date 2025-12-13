export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  due_date?: string;
  priority?: "low" | "medium" | "high";
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface ApiError {
  detail: string;
}