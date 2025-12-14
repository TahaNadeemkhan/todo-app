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
import { toast } from "sonner";
import { Task } from "@/lib/types";
import { Plus } from "lucide-react";
import { motion } from "framer-motion";

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
      });
      onTaskAdded(response.data);
      setOpen(false);
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setDueTime("");
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