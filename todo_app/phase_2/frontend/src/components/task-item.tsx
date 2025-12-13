"use client";

import { useState } from "react";
import { Task } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2, Calendar as CalendarIcon, Flag, AlertCircle, Clock } from "lucide-react";
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
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9 }}
        whileHover={{ scale: 1.02, y: -4, transition: { type: "spring", stiffness: 400, damping: 10 } }}
        className="group"
      >
        <Card className="mb-4 overflow-hidden border-border bg-card/95 backdrop-blur-md shadow-sm hover:shadow-lg hover:shadow-primary/10 transition-all duration-300">
          <CardContent className="flex items-start p-5 gap-4">
            <motion.div whileTap={{ scale: 0.8 }}>
              <Checkbox 
                checked={task.completed} 
                onCheckedChange={handleToggleComplete}
                className="mt-1 data-[state=checked]:bg-primary data-[state=checked]:border-primary border-muted-foreground/30 h-5 w-5 rounded-md" 
              />
            </motion.div>
            
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <h3 className={`font-semibold text-lg transition-all duration-300 ${task.completed ? "line-through text-muted-foreground decoration-2" : "text-foreground"}`}>
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
                <p className="text-sm text-muted-foreground leading-relaxed">{task.description}</p>
              )}
              
              <div className="flex items-center gap-3 mt-3 flex-wrap">
                {task.priority && (
                  <div className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${
                    task.priority === 'high' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                    task.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                    'bg-blue-500/10 text-blue-500 border-blue-500/20'
                  }`}>
                    <Flag className="w-3 h-3" />
                    <span className="capitalize">{task.priority}</span>
                  </div>
                )}
                {task.due_date && (
                  <div className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${
                    isDueSoon()
                      ? 'bg-orange-500/20 text-orange-600 border-orange-500/30 animate-pulse'
                      : 'text-muted-foreground/70 bg-white/10 border-white/10'
                  }`}>
                    <CalendarIcon className="w-3 h-3" />
                    <span className="font-medium">
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
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-600 border border-orange-500/30"
                  >
                    <AlertCircle className="w-3 h-3" />
                    <span className="font-medium">Due Soon!</span>
                  </motion.div>
                )}
                <div className="flex items-center gap-1 text-xs text-muted-foreground/60 ml-auto">
                  <Clock className="w-3 h-3" />
                  <span>
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
