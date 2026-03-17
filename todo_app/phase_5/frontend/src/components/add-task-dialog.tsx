"use client";

import { useState, FormEvent } from "react";
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
import { Plus, ChevronDown, ChevronRight, Bell, Repeat } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { RecurrenceConfigDialog, RecurrenceConfig } from "@/components/recurrence-config-dialog";
import { RecurrenceBadge } from "@/components/recurrence-badge";
import { PrioritySelector, Priority } from "@/components/priority-selector";
import { TagInput } from "@/components/tag-input";
import { DueDateTimePicker } from "@/components/due-date-time-picker";
import { ReminderConfig, ReminderOption } from "@/components/reminder-config";

interface AddTaskDialogProps {
  onTaskAdded: (task: Task) => void;
}

export function AddTaskDialog({ onTaskAdded }: AddTaskDialogProps) {
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [tags, setTags] = useState<string[]>([]);
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Advanced settings
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [notifyEmail, setNotifyEmail] = useState("");
  const [reminders, setReminders] = useState<ReminderOption[]>([]);

  // Recurrence configuration
  const [recurrenceConfig, setRecurrenceConfig] = useState<RecurrenceConfig | null>(null);
  const [showRecurrenceDialog, setShowRecurrenceDialog] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
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
          dueDateTimeISO = new Date(`${dueDate}T${dueTime}`).toISOString();
        } else {
          dueDateTimeISO = new Date(dueDate).toISOString();
        }
      }

      const response = await apiClient.post<Task>(`/api/${session.user.id}/tasks`, {
        title,
        description: description || undefined,
        priority,
        tags,
        due_date: dueDateTimeISO,
        notifications_enabled: notificationsEnabled,
        notify_email: notificationsEnabled && notifyEmail ? notifyEmail : undefined,
        reminders: reminders.length > 0 ? reminders : undefined,
        recurrence: recurrenceConfig ? {
          pattern: recurrenceConfig.pattern,
          interval: recurrenceConfig.interval,
          days_of_week: recurrenceConfig.days_of_week,
          day_of_month: recurrenceConfig.day_of_month,
        } : undefined,
      });

      onTaskAdded(response.data);
      setOpen(false);

      // Reset form
      setTitle("");
      setDescription("");
      setPriority("medium");
      setTags([]);
      setDueDate("");
      setDueTime("");
      setNotificationsEnabled(false);
      setNotifyEmail("");
      setReminders([]);
      setShowAdvanced(false);
      setRecurrenceConfig(null);

      toast.success("Task created");
    } catch (error) {
      console.error("Failed to create task", error);
      toast.error("Failed to create task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Plus className="mr-2 h-4 w-4" /> Add Task
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px] bg-card border-border max-h-[90vh] overflow-y-auto">
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
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Priority</Label>
                  <PrioritySelector
                    value={priority}
                    onChange={setPriority}
                    className="w-full"
                  />
                </div>
                <div className="grid gap-2">
                  <Label>Tags</Label>
                  <TagInput
                    value={tags}
                    onChange={setTags}
                    placeholder="e.g. work, urgent"
                  />
                </div>
              </div>
              
              <DueDateTimePicker 
                date={dueDate}
                time={dueTime}
                onDateChange={setDueDate}
                onTimeChange={setDueTime}
              />

              {/* Recurrence Configuration */}
              <div className="border-t border-border pt-4 mt-2">
                <button
                  type="button"
                  onClick={() => setShowRecurrenceDialog(true)}
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full mb-3"
                >
                  <Repeat className="h-4 w-4" />
                  <span>Recurrence Settings</span>
                  {recurrenceConfig && (
                    <RecurrenceBadge recurrence={recurrenceConfig} className="ml-auto" />
                  )}
                </button>
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
                  <span>Notification & Reminders</span>
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
                      <div className="pt-4 space-y-6">
                        <div className="space-y-4">
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
                              Enable basic email notifications
                            </Label>
                          </div>

                          {notificationsEnabled && (
                            <motion.div
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="grid gap-2"
                            >
                              <Label htmlFor="notifyEmail" className="text-[10px] uppercase text-muted-foreground">Notification Email</Label>
                              <Input
                                id="notifyEmail"
                                type="email"
                                placeholder="Enter email for notifications"
                                value={notifyEmail}
                                onChange={(e) => setNotifyEmail(e.target.value)}
                                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
                              />
                            </motion.div>
                          )}
                        </div>

                        <div className="border-t border-border pt-4">
                          <ReminderConfig 
                            reminders={reminders}
                            onChange={setReminders}
                            disabled={!dueDate}
                          />
                          {!dueDate && (
                            <p className="text-[10px] text-muted-foreground mt-2 italic">
                              Set a due date first to configure reminders.
                            </p>
                          )}
                        </div>
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

      {/* Recurrence Configuration Dialog */}
      <RecurrenceConfigDialog
        open={showRecurrenceDialog}
        onOpenChange={setShowRecurrenceDialog}
        onSave={setRecurrenceConfig}
        initialConfig={recurrenceConfig}
      />
    </>
  );
}