"use client";

import { Task } from "@/lib/types";
import { TaskItem } from "./task-item";
import { AnimatePresence, motion } from "framer-motion";
import { useSearchParams } from "next/navigation";
import { Calendar } from "lucide-react";

interface TaskListProps {
  tasks: Task[];
  onTaskUpdated: (task: Task) => void;
  onTaskDeleted: (taskId: number) => void;
  filter?: string | null;
}

// Group tasks by date periods for Upcoming view
function groupTasksByPeriod(tasks: Task[]) {
  const now = new Date();
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const tomorrowEnd = new Date(tomorrow);
  tomorrowEnd.setDate(tomorrowEnd.getDate() + 1); // Day after tomorrow

  const weekEnd = new Date(today);
  weekEnd.setDate(weekEnd.getDate() + 7);

  const groups: { [key: string]: Task[] } = {
    overdue: [],
    today: [],
    tomorrow: [],
    thisWeek: [],
    later: [],
  };

  tasks.forEach((task) => {
    if (!task.due_date) return;

    const taskDate = new Date(task.due_date);
    taskDate.setHours(0, 0, 0, 0);

    const taskTime = taskDate.getTime();
    const todayTime = today.getTime();
    const tomorrowTime = tomorrow.getTime();
    const tomorrowEndTime = tomorrowEnd.getTime();
    const weekEndTime = weekEnd.getTime();

    if (taskTime < todayTime) {
      groups.overdue.push(task);
    } else if (taskTime === todayTime) {
      groups.today.push(task);
    } else if (taskTime >= tomorrowTime && taskTime < tomorrowEndTime) {
      groups.tomorrow.push(task);
    } else if (taskTime >= tomorrowEndTime && taskTime <= weekEndTime) {
      groups.thisWeek.push(task);
    } else if (taskTime > weekEndTime) {
      groups.later.push(task);
    }
  });

  return groups;
}

export function TaskList({ tasks, onTaskUpdated, onTaskDeleted, filter: filterProp }: TaskListProps) {
  const searchParams = useSearchParams();
  const filter = filterProp ?? searchParams.get("filter");

  if (tasks.length === 0) {
    let message = "No tasks found.";
    let subMessage = "Add one to get started!";

    if (filter === "today") {
      message = "No tasks due today.";
      subMessage = "Enjoy your day!";
    } else if (filter === "upcoming") {
      message = "No upcoming tasks.";
      subMessage = "You're all caught up!";
    } else if (filter === "completed") {
      message = "No completed tasks yet.";
      subMessage = "Get to work!";
    }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-16"
      >
        <div className="inline-block">
          <p className="text-muted-foreground font-medium text-lg">{message}</p>
          <p className="text-sm text-muted-foreground mt-1">{subMessage}</p>
        </div>
      </motion.div>
    );
  }

  // Grouped view for Upcoming tab
  if (filter === "upcoming") {
    const grouped = groupTasksByPeriod(tasks);

    return (
      <div className="space-y-6">
        {/* Overdue Section */}
        {grouped.overdue.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-red-600">Overdue</h2>
              <span className="text-xs text-muted-foreground">
                {grouped.overdue.length}
              </span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {grouped.overdue.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onUpdate={onTaskUpdated}
                    onDelete={onTaskDeleted}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* Today Section */}
        {grouped.today.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-primary">Today</h2>
              <span className="text-xs text-muted-foreground">
                {grouped.today.length}
              </span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {grouped.today.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onUpdate={onTaskUpdated}
                    onDelete={onTaskDeleted}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* Tomorrow Section */}
        {grouped.tomorrow.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-foreground">Tomorrow</h2>
              <span className="text-xs text-muted-foreground">
                {grouped.tomorrow.length}
              </span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {grouped.tomorrow.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onUpdate={onTaskUpdated}
                    onDelete={onTaskDeleted}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* This Week Section */}
        {grouped.thisWeek.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-foreground">This Week</h2>
              <span className="text-xs text-muted-foreground">
                {grouped.thisWeek.length}
              </span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {grouped.thisWeek.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onUpdate={onTaskUpdated}
                    onDelete={onTaskDeleted}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* Later Section */}
        {grouped.later.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-foreground">Later</h2>
              <span className="text-xs text-muted-foreground">
                {grouped.later.length}
              </span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {grouped.later.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onUpdate={onTaskUpdated}
                    onDelete={onTaskDeleted}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default list view for other tabs
  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onUpdate={onTaskUpdated}
            onDelete={onTaskDeleted}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
