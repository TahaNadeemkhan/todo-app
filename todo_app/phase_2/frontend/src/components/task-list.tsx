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
        className="text-center py-20"
      >
        <div className="glass-panel inline-block px-8 py-6">
          <p className="text-muted-foreground font-medium">{message}</p>
          <p className="text-sm text-muted-foreground/60 mt-1">{subMessage}</p>
        </div>
      </motion.div>
    );
  }

  // Grouped view for Upcoming tab
  if (filter === "upcoming") {
    const grouped = groupTasksByPeriod(tasks);

    return (
      <div className="space-y-8">
        {/* Overdue Section */}
        {grouped.overdue.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-red-500/20">
              <Calendar className="w-5 h-5 text-red-600" />
              <h2 className="text-xl font-bold text-foreground">Overdue</h2>
              <span className="text-sm font-medium text-red-600 bg-red-500/10 px-2 py-0.5 rounded-full">
                {grouped.overdue.length} {grouped.overdue.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>
            <div className="space-y-4">
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
          </motion.div>
        )}

        {/* Today Section */}
        {grouped.today.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-green-500/20">
              <Calendar className="w-5 h-5 text-green-600" />
              <h2 className="text-xl font-bold text-foreground">Today</h2>
              <span className="text-sm font-medium text-green-600 bg-green-500/10 px-2 py-0.5 rounded-full">
                {grouped.today.length} {grouped.today.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>
            <div className="space-y-4">
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
          </motion.div>
        )}

        {/* Tomorrow Section */}
        {grouped.tomorrow.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-orange-500/20">
              <Calendar className="w-5 h-5 text-orange-600" />
              <h2 className="text-xl font-bold text-foreground">Tomorrow</h2>
              <span className="text-sm font-medium text-orange-600 bg-orange-500/10 px-2 py-0.5 rounded-full">
                {grouped.tomorrow.length} {grouped.tomorrow.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>
            <div className="space-y-4">
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
          </motion.div>
        )}

        {/* This Week Section */}
        {grouped.thisWeek.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-blue-500/20">
              <Calendar className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-bold text-foreground">This Week</h2>
              <span className="text-sm font-medium text-blue-600 bg-blue-500/10 px-2 py-0.5 rounded-full">
                {grouped.thisWeek.length} {grouped.thisWeek.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>
            <div className="space-y-4">
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
          </motion.div>
        )}

        {/* Later Section */}
        {grouped.later.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-purple-500/20">
              <Calendar className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-bold text-foreground">Later</h2>
              <span className="text-sm font-medium text-purple-600 bg-purple-500/10 px-2 py-0.5 rounded-full">
                {grouped.later.length} {grouped.later.length === 1 ? 'task' : 'tasks'}
              </span>
            </div>
            <div className="space-y-4">
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
          </motion.div>
        )}
      </div>
    );
  }

  // Default list view for other tabs
  return (
    <div className="space-y-4">
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
