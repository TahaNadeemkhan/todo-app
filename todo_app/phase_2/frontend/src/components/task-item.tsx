"use client";

import { Task } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";

interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
  return (
    <Card className="mb-4">
      <CardContent className="flex items-start p-4 gap-4">
        <Checkbox checked={task.completed} className="mt-1" disabled />
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className={`font-semibold ${task.completed ? "line-through text-gray-500" : ""}`}>
              {task.title}
            </h3>
            <span className="text-xs text-gray-400">
              {new Date(task.created_at).toLocaleDateString()}
            </span>
          </div>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
