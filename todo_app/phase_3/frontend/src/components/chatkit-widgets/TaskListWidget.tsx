/**
 * Task List Widget for ChatKit
 * Displays tasks in a beautiful card-based UI instead of raw JSON
 */

import { Check, Circle, Clock, AlertCircle } from "lucide-react";

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: "low" | "medium" | "high";
  due_date?: string;
}

interface TaskListWidgetProps {
  tasks: Task[];
  title?: string;
}

export function TaskListWidget({ tasks, title = "Your Tasks" }: TaskListWidgetProps) {
  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case "high":
        return "text-red-500 bg-red-50 dark:bg-red-900/20";
      case "medium":
        return "text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20";
      case "low":
        return "text-blue-500 bg-blue-50 dark:bg-blue-900/20";
      default:
        return "text-gray-500 bg-gray-50 dark:bg-gray-900/20";
    }
  };

  const getPriorityIcon = (priority?: string) => {
    switch (priority) {
      case "high":
        return <AlertCircle className="h-4 w-4" />;
      case "medium":
        return <Clock className="h-4 w-4" />;
      default:
        return <Circle className="h-4 w-4" />;
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="p-6 text-center bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <Circle className="h-12 w-12 mx-auto mb-3 text-gray-400" />
        <p className="text-gray-600 dark:text-gray-400">No tasks found</p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
          Add your first task to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {tasks.filter(t => !t.completed).length} active
        </span>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`group p-3 rounded-lg border transition-all ${
              task.completed
                ? "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 opacity-60"
                : "bg-white dark:bg-gray-850 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
            }`}
          >
            <div className="flex items-start gap-3">
              {/* Checkbox Icon */}
              <div className="flex-shrink-0 mt-0.5">
                {task.completed ? (
                  <Check className="h-5 w-5 text-green-500" />
                ) : (
                  <Circle className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
                )}
              </div>

              {/* Task Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4
                    className={`font-medium ${
                      task.completed
                        ? "line-through text-gray-500 dark:text-gray-400"
                        : "text-gray-900 dark:text-gray-100"
                    }`}
                  >
                    {task.title}
                  </h4>
                  {task.priority && (
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(
                        task.priority
                      )}`}
                    >
                      {getPriorityIcon(task.priority)}
                      {task.priority}
                    </span>
                  )}
                </div>

                {task.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {task.description}
                  </p>
                )}

                {task.due_date && (
                  <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                    <Clock className="h-3 w-3" />
                    <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            {tasks.filter(t => t.completed).length} of {tasks.length} completed
          </span>
          <div className="h-2 w-32 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all"
              style={{
                width: `${(tasks.filter(t => t.completed).length / tasks.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
