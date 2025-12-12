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
import { toast } from "sonner";
import { Task } from "@/lib/types";

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
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setTitle(task.title);
    setDescription(task.description || "");
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      toast.error("Title is required");
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.put<Task>(`/api/${session?.user?.id}/tasks/${task.id}`, {
        title,
        description: description || undefined,
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
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Make changes to your task here.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-title" className="text-right">
                Title
              </Label>
              <Input
                id="edit-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-description" className="text-right">
                Desc
              </Label>
              <Input
                id="edit-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="col-span-3"
                placeholder="Optional"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
