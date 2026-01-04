"use client";

import { useState } from "react";
import { Task } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2, Calendar as CalendarIcon, Flag, AlertCircle, Clock, CheckCircle2, Circle } from "lucide-react";
import { EditTaskDialog } from "./edit-task-dialog";
import { DeleteConfirmDialog } from "./delete-confirm-dialog";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { toast } from "sonner";
import { motion } from "framer-motion";

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
    if (!session?.user?.id) {
      toast.error("You must be logged in to delete tasks");
      return;
    }

    try {
      await apiClient.delete(`/api/${session.user.id}/tasks/${task.id}`);
      onDelete(task.id);
      toast.success("Task deleted");
    } catch (error) {
      console.error("Failed to delete task", error);
      toast.error("Failed to delete task");
    }
  };

  const handleToggleComplete = async (checked: boolean) => {
    if (!session?.user?.id) {
      toast.error("You must be logged in to update tasks");
      return;
    }

    // Optimistic Update
    const updatedTask = { ...task, completed: checked };
    onUpdate(updatedTask);

    try {
      await apiClient.patch(`/api/${session.user.id}/tasks/${task.id}/complete`);
    } catch (error) {
      console.error("Failed to toggle task", error);
      toast.error("Failed to update task");
      // Rollback
      onUpdate(task);
    }
  };

  // Check if task is due within 24 hours OR due today
  const isDueSoon = () => {
    if (!task.due_date || task.completed) return false;

    const dueDate = new Date(task.due_date);
    const now = new Date();

    // Check if due today
    const today = new Date(now);
    today.setHours(0, 0, 0, 0);
    const dueDateOnly = new Date(dueDate);
    dueDateOnly.setHours(0, 0, 0, 0);

    if (dueDateOnly.getTime() === today.getTime()) {
      return true; // Due today = always show warning
    }

    // Check if due within next 24 hours
    const hoursUntilDue = (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60);
    return hoursUntilDue > 0 && hoursUntilDue <= 24;
  };

  return (
    <>
      <motion.div
        layout
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="group h-full"
      >
        <Card className={`h-full overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 relative ${
          task.completed
            ? 'border-green-500/30 bg-green-50 dark:bg-green-950/20'
            : 'border-border bg-card'
        }`}>
          <CardContent className="flex flex-col p-4 gap-3 h-full">
            {/* Header with checkbox and title */}
            <div className="flex items-start gap-3">
              <motion.button
                whileTap={{ scale: 0.85 }}
                whileHover={{ scale: 1.1 }}
                onClick={() => handleToggleComplete(!task.completed)}
                className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-300 cursor-pointer ${
                  task.completed
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'border-muted-foreground/40 hover:border-primary hover:bg-primary/10'
                }`}
                title={task.completed ? "Mark as incomplete" : "Mark as complete"}
              >
                {task.completed && <CheckCircle2 className="w-3.5 h-3.5" />}
              </motion.button>

              <div className="flex-1 min-w-0">
                <h3 className={`font-medium text-base transition-all duration-300 line-clamp-2 ${task.completed ? "line-through text-muted-foreground" : "text-foreground"}`}>
                  {task.title}
                </h3>
              </div>
            </div>

            {/* Description */}
            {task.description && (
              <p className="text-sm text-foreground/60 dark:text-foreground/50 line-clamp-2 leading-relaxed">
                {task.description}
              </p>
            )}

            {/* Spacer to push badges to bottom */}
            <div className="flex-1" />

            {/* Badges at bottom */}
            <div className="flex flex-col gap-2 mt-auto">
              {task.priority && (
                <div className={`flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-md w-fit ${
                  task.priority === 'high' ? 'bg-red-500/15 text-red-600 dark:text-red-400' :
                  task.priority === 'medium' ? 'bg-yellow-500/15 text-yellow-600 dark:text-yellow-400' :
                  'bg-blue-500/15 text-blue-600 dark:text-blue-400'
                }`}>
                  <Flag className="w-3 h-3" />
                  <span className="capitalize">{task.priority}</span>
                </div>
              )}

              {task.due_date && (
                <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-md w-fit ${
                  isDueSoon()
                    ? 'bg-orange-100 dark:bg-orange-950 text-orange-600 dark:text-orange-400'
                    : 'text-foreground/60 bg-muted/50'
                }`}>
                  <CalendarIcon className="w-3 h-3" />
                  <span>
                    {new Date(task.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  </span>
                </div>
              )}
            </div>

            {/* Action buttons on hover */}
            <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <Button variant="ghost" size="icon" onClick={() => setIsEditOpen(true)} className="h-7 w-7 hover:bg-primary/10 hover:text-primary">
                <Pencil className="h-3.5 w-3.5" />
              </Button>
              <Button variant="ghost" size="icon" onClick={() => setIsDeleteOpen(true)} className="h-7 w-7 hover:bg-destructive/10 hover:text-destructive">
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

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
