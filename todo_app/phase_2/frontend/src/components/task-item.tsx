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
        className="group"
      >
        <Card className={`mb-3 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 ${
          task.completed
            ? 'border-green-500/30 bg-green-50 dark:bg-green-950/20'
            : 'border-border bg-card'
        }`}>
          <CardContent className="flex items-start p-5 gap-4">
            {/* Custom Checkbox with better UX */}
            <motion.button
              whileTap={{ scale: 0.85 }}
              whileHover={{ scale: 1.1 }}
              onClick={() => handleToggleComplete(!task.completed)}
              className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 cursor-pointer ${
                task.completed
                  ? 'bg-green-500 border-green-500 text-white shadow-lg shadow-green-500/30'
                  : 'border-muted-foreground/40 hover:border-primary hover:bg-primary/10'
              }`}
              title={task.completed ? "Mark as incomplete" : "Mark as complete"}
            >
              {task.completed ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <Circle className="w-4 h-4 opacity-0 group-hover:opacity-30" />
              )}
            </motion.button>

            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between gap-2">
                {/* Completed Badge */}
                {task.completed && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Completed</span>
                  </motion.div>
                )}
                <h3 className={`font-semibold text-lg transition-all duration-300 flex-1 ${task.completed ? "line-through text-muted-foreground decoration-2" : "text-foreground"}`}>
                  {task.title}
                </h3>
                
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <motion.div whileHover={{ rotate: 8, scale: 1.1 }}>
                    <Button variant="ghost" size="icon" onClick={() => setIsEditOpen(true)} className="h-8 w-8 hover:bg-primary/10 hover:text-primary">
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </motion.div>
                  <motion.div whileHover={{ rotate: -8, scale: 1.1, color: "#ef4444" }}>
                    <Button variant="ghost" size="icon" onClick={() => setIsDeleteOpen(true)} className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </motion.div>
                </div>
              </div>
              
              {task.description && (
                <p className="text-sm text-foreground/70 dark:text-foreground/60 leading-relaxed">{task.description}</p>
              )}
              
              <div className="flex items-center gap-3 mt-3 flex-wrap">
                {task.priority && (
                  <div className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${
                    task.priority === 'high' ? 'bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30' :
                    task.priority === 'medium' ? 'bg-yellow-500/15 text-yellow-600 dark:text-yellow-400 border-yellow-500/30' :
                    'bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30'
                  }`}>
                    <Flag className="w-3 h-3" />
                    <span className="capitalize">{task.priority}</span>
                  </div>
                )}
                {task.due_date && (
                  <div className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full border ${
                    isDueSoon()
                      ? 'bg-orange-100 dark:bg-orange-950 text-orange-600 dark:text-orange-400 border-orange-500/30'
                      : 'text-foreground/70 dark:text-foreground/60 bg-muted/50 border-border'
                  }`}>
                    <CalendarIcon className="w-3 h-3" />
                    <span>
                      Due: {new Date(task.due_date).toLocaleDateString()}
                      {(() => {
                        const date = new Date(task.due_date);
                        const hours = date.getHours();
                        const minutes = date.getMinutes();
                        // Show time only if it's not midnight (00:00) in local timezone
                        if (hours !== 0 || minutes !== 0) {
                          return ` · ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                        }
                        return '';
                      })()}
                    </span>
                  </div>
                )}
                {isDueSoon() && (
                  <div className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-orange-100 dark:bg-orange-950 text-orange-600 dark:text-orange-400 border border-orange-500/30">
                    <AlertCircle className="w-3 h-3" />
                    <span className="font-medium">Due Soon!</span>
                  </div>
                )}
                <div className="flex items-center gap-1.5 text-xs text-foreground/50 dark:text-foreground/40 ml-auto bg-muted/30 px-2 py-1 rounded-full">
                  <Clock className="w-3 h-3" />
                  <span className="font-medium">
                    Created {new Date(task.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  </span>
                </div>
              </div>
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
