"use client";

import { useEffect, useState } from "react";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { Task } from "@/lib/types";
import { TaskList } from "@/components/task-list";
import { LogoutButton } from "@/components/logout-button";
import { AddTaskDialog } from "@/components/add-task-dialog";
import { toast } from "sonner";

export default function DashboardPage() {
  const { data: session } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (session?.user?.id) {
      fetchTasks();
    }
  }, [session?.user?.id]);

  const fetchTasks = async () => {
    try {
      // session.user.id is the user_id for the API path
      const response = await apiClient.get<Task[]>(`/api/${session?.user?.id}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error("Failed to fetch tasks", error);
      toast.error("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskAdded = (task: Task) => {
    setTasks([task, ...tasks]);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading tasks...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
          <div className="flex items-center gap-4">
            <AddTaskDialog onTaskAdded={handleTaskAdded} />
            <span className="text-sm text-gray-600">{session?.user?.name}</span>
            <LogoutButton />
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <TaskList tasks={tasks} />
      </main>
    </div>
  );
}
