"use client";

import { useState, useEffect } from "react";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { Task } from "@/lib/types";
import { ChevronDown, ChevronRight, Bell } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface EditTaskDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskUpdated: (task: Task) => void;
}

export function EditTaskDialog({ task, open, onOpenChange, onTaskUpdated }: EditTaskDialogProps) {
  const { data: session } = useSession();
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || "");
  const [priority, setPriority] = useState<"low" | "medium" | "high">(task.priority || "medium");
  const [dueDate, setDueDate] = useState(task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : "");
  const [dueTime, setDueTime] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Advanced settings
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(task.notifications_enabled || false);
  const [notifyEmail, setNotifyEmail] = useState(task.notify_email || "");

  useEffect(() => {
    setTitle(task.title);
    setDescription(task.description || "");
    setPriority(task.priority || "medium");
    setNotificationsEnabled(task.notifications_enabled || false);
    setNotifyEmail(task.notify_email || "");

    if (task.due_date) {
      const date = new Date(task.due_date);

      // Extract date in local timezone
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      setDueDate(`${year}-${month}-${day}`);

      // Extract time in local timezone (not UTC)
      const hours = date.getHours();
      const minutes = date.getMinutes();
      if (hours !== 0 || minutes !== 0) {
        setDueTime(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`);
      } else {
        setDueTime("");
      }
    } else {
      setDueDate("");
      setDueTime("");
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!session?.user?.id) {
      toast.error("You must be logged in to update tasks");
      return;
    }

    if (!title.trim()) {
      toast.error("Title is required");
      return;
    }

    setIsLoading(true);
    try {
      // Combine date and time if both provided
      let dueDateTimeISO: string | undefined = undefined;
      if (dueDate) {
        if (dueTime) {
          // Combine date + time
          dueDateTimeISO = new Date(`${dueDate}T${dueTime}`).toISOString();
        } else {
          // Date only - set to start of day
          dueDateTimeISO = new Date(dueDate).toISOString();
        }
      }

      const response = await apiClient.put<Task>(`/api/${session.user.id}/tasks/${task.id}`, {
        title,
        description: description || undefined,
        priority,
        due_date: dueDateTimeISO,
        notifications_enabled: notificationsEnabled,
        notify_email: notificationsEnabled && notifyEmail ? notifyEmail : null,
      });
      onTaskUpdated(response.data);
      onOpenChange(false);
      toast.success("Task updated");
    } catch (error) {
      console.error("Failed to update task", error);
      toast.error("Failed to update task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border-white/20 shadow-2xl">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Make changes to your task here.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-description">Description</Label>
              <Input
                id="edit-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional"
                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-priority">Priority</Label>
              <select
                id="edit-priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as any)}
                className="flex h-9 w-full items-center justify-between rounded-md border border-white/20 bg-white/50 dark:bg-zinc-800 dark:text-white px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="low" className="bg-white dark:bg-zinc-800">Low</option>
                <option value="medium" className="bg-white dark:bg-zinc-800">Medium</option>
                <option value="high" className="bg-white dark:bg-zinc-800">High</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-dueDate">Due Date</Label>
                <Input
                  id="edit-dueDate"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-dueTime" className="flex items-center gap-1">
                  Due Time <span className="text-xs text-muted-foreground">(Optional)</span>
                </Label>
                <Input
                  id="edit-dueTime"
                  type="time"
                  value={dueTime}
                  onChange={(e) => setDueTime(e.target.value)}
                  disabled={!dueDate}
                  className="bg-white/50 border-white/20 focus:border-primary/50 transition-all disabled:opacity-50"
                />
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="border-t border-border pt-4 mt-2">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full"
              >
                {showAdvanced ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                <Bell className="h-4 w-4" />
                <span>Notification Settings</span>
              </button>

              <AnimatePresence>
                {showAdvanced && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="pt-4 space-y-4">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="edit-notifications"
                          checked={notificationsEnabled}
                          onCheckedChange={(checked) => {
                            setNotificationsEnabled(checked === true);
                            if (!checked) setNotifyEmail("");
                          }}
                        />
                        <Label
                          htmlFor="edit-notifications"
                          className="text-sm font-normal cursor-pointer"
                        >
                          Enable email notifications for this task
                        </Label>
                      </div>

                      {notificationsEnabled && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="grid gap-2"
                        >
                          <Label htmlFor="edit-notifyEmail">Notification Email</Label>
                          <Input
                            id="edit-notifyEmail"
                            type="email"
                            placeholder="Enter email for notifications"
                            value={notifyEmail}
                            onChange={(e) => setNotifyEmail(e.target.value)}
                            className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
                          />
                          <p className="text-xs text-muted-foreground">
                            You'll receive emails when this task is updated or completed.
                          </p>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isLoading} className="w-full rounded-full">
              {isLoading ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}