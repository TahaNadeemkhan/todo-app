export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  due_date?: string;
  priority?: "low" | "medium" | "high";
  // Notification settings
  notify_email?: string;
  notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  user_id: string;
  task_id?: number;
  type: string;
  title: string;
  message: string;
  email_sent_to: string;
  is_read: boolean;
  sent_at: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface ApiError {
  detail: string;
}