"use client";

import { useState } from "react";
import { Task } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2 } from "lucide-react";
import { EditTaskDialog } from "./edit-task-dialog";
import { DeleteConfirmDialog } from "./delete-confirm-dialog";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { toast } from "sonner";

interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: number) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const { data: session } = useSession();

  const handleDelete = async () => {
    try {
      await apiClient.delete(`/api/${session?.user?.id}/tasks/${task.id}`);
      onDelete(task.id);
      toast.success("Task deleted");
    } catch (error) {
      console.error("Failed to delete task", error);
      toast.error("Failed to delete task");
    }
  };

  const handleToggleComplete = async (checked: boolean) => {
    // Optimistic Update
    const updatedTask = { ...task, completed: checked };
    onUpdate(updatedTask);

    try {
      await apiClient.patch(`/api/${session?.user?.id}/tasks/${task.id}/complete`);
    } catch (error) {
      console.error("Failed to toggle task", error);
      toast.error("Failed to update task");
      // Rollback
      onUpdate(task);
    }
  };

  return (
    <>
      <Card className="mb-4">
        <CardContent className="flex items-start p-4 gap-4">
          <Checkbox 
            checked={task.completed} 
            onCheckedChange={handleToggleComplete}
            className="mt-1" 
          />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className={`font-semibold ${task.completed ? "line-through text-gray-500" : ""}`}>
                {task.title}
              </h3>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => setIsEditOpen(true)}>
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setIsDeleteOpen(true)} className="text-red-500 hover:text-red-600 hover:bg-red-50">
                  <Trash2 className="h-4 w-4" />
                </Button>
                <span className="text-xs text-gray-400">
                  {new Date(task.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            {task.description && (
              <p className="text-sm text-gray-600 mt-1">{task.description}</p>
            )}
          </div>
        </CardContent>
      </Card>

      <EditTaskDialog 
        task={task} 
        open={isEditOpen} 
        onOpenChange={setIsEditOpen} 
        onTaskUpdated={onUpdate}
      />

      <DeleteConfirmDialog 
        open={isDeleteOpen} 
        onOpenChange={setIsDeleteOpen} 
        onConfirm={handleDelete}
        title={`Delete "${task.title}"?`}
      />
    </>
  );
}