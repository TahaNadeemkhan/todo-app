"use client";

import { useState } from "react";
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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { Task } from "@/lib/types";
import { Plus, ChevronDown, ChevronRight, Bell } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface AddTaskDialogProps {
  onTaskAdded: (task: Task) => void;
}

export function AddTaskDialog({ onTaskAdded }: AddTaskDialogProps) {
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Advanced settings
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [notifyEmail, setNotifyEmail] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!session?.user?.id) {
      toast.error("You must be logged in to add tasks");
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

      const response = await apiClient.post<Task>(`/api/${session.user.id}/tasks`, {
        title,
        description: description || undefined,
        priority,
        due_date: dueDateTimeISO,
        notifications_enabled: notificationsEnabled,
        notify_email: notificationsEnabled && notifyEmail ? notifyEmail : undefined,
      });
      onTaskAdded(response.data);
      setOpen(false);
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setDueTime("");
      setNotificationsEnabled(false);
      setNotifyEmail("");
      setShowAdvanced(false);
      toast.success("Task created");
    } catch (error) {
      console.error("Failed to create task", error);
      toast.error("Failed to create task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
          <Plus className="mr-2 h-4 w-4" /> Add Task
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] bg-card border-border">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add Task</DialogTitle>
            <DialogDescription>
              Create a new task to track your work.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional"
                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as any)}
                className="flex h-9 w-full items-center justify-between rounded-md border border-white/20 bg-white/50 px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="dueDate">Due Date</Label>
                <Input
                  id="dueDate"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="dueTime" className="flex items-center gap-1">
                  Due Time <span className="text-xs text-muted-foreground">(Optional)</span>
                </Label>
                <Input
                  id="dueTime"
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
                          id="notifications"
                          checked={notificationsEnabled}
                          onCheckedChange={(checked) => {
                            setNotificationsEnabled(checked === true);
                            if (!checked) setNotifyEmail("");
                          }}
                        />
                        <Label
                          htmlFor="notifications"
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
                          <Label htmlFor="notifyEmail">Notification Email</Label>
                          <Input
                            id="notifyEmail"
                            type="email"
                            placeholder="Enter email for notifications"
                            value={notifyEmail}
                            onChange={(e) => setNotifyEmail(e.target.value)}
                            className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
                          />
                          <p className="text-xs text-muted-foreground">
                            You'll receive emails when this task is created, updated, or completed.
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
              {isLoading ? "Saving..." : "Save Task"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}