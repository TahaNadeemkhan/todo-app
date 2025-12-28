"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { Task } from "@/lib/types";
import { TaskList } from "@/components/task-list";
import { AddTaskDialog } from "@/components/add-task-dialog";
import { SearchAndFilterBar } from "@/components/search-and-filter-bar";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";

interface DashboardContentProps {
  forcedFilter?: string;
  pageTitle?: string;
}

export function DashboardContent({ forcedFilter, pageTitle }: DashboardContentProps) {
  const { data: session } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const searchParams = useSearchParams();

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "completed" | "incomplete">("all");
  const [priorityFilter, setPriorityFilter] = useState<"all" | "high" | "medium" | "low">("all");

  const filter = forcedFilter || searchParams.get("filter");

  useEffect(() => {
    if (session?.user?.id) {
      fetchTasks();
    }
  }, [session?.user?.id]);

  const fetchTasks = async (showToast = false) => {
    if (showToast) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const response = await apiClient.get<Task[]>(`/api/${session?.user?.id}/tasks`);
      setTasks(response.data);
      if (showToast) {
        toast.success("Tasks refreshed");
      }
    } catch (error) {
      console.error("Failed to fetch tasks", error);
      toast.error("Failed to load tasks");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleTaskAdded = (task: Task) => {
    setTasks([task, ...tasks]);
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
  };

  const handleTaskDeleted = (taskId: number) => {
    setTasks(tasks.filter((t) => t.id !== taskId));
  };

  const filteredTasks = tasks.filter((task) => {
    // Step 1: Apply view-based filters (today, upcoming, completed)
    if (filter === "completed") {
      if (!task.completed) return false;
    }

    // Parse dates for date-based filters
    const taskDate = task.due_date ? new Date(task.due_date) : null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (filter === "today") {
      if (!taskDate) return false;
      const tDate = new Date(taskDate);
      tDate.setHours(0, 0, 0, 0);
      if (tDate.getTime() !== today.getTime()) return false;
    }

    if (filter === "upcoming") {
      if (!taskDate) return false;
      const tDate = new Date(taskDate);
      tDate.setHours(0, 0, 0, 0);
      if (tDate.getTime() < today.getTime()) return false;
    }

    // Step 2: Apply search query (title or description)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchesTitle = task.title.toLowerCase().includes(query);
      const matchesDescription = task.description?.toLowerCase().includes(query) ?? false;
      if (!matchesTitle && !matchesDescription) return false;
    }

    // Step 3: Apply status filter
    if (statusFilter === "completed" && !task.completed) return false;
    if (statusFilter === "incomplete" && task.completed) return false;

    // Step 4: Apply priority filter
    if (priorityFilter !== "all" && task.priority !== priorityFilter) return false;

    return true;
  }).sort((a, b) => {
    // Sort upcoming tasks by due_date (earliest first)
    if (filter === "upcoming") {
      const dateA = a.due_date ? new Date(a.due_date).getTime() : Number.MAX_SAFE_INTEGER;
      const dateB = b.due_date ? new Date(b.due_date).getTime() : Number.MAX_SAFE_INTEGER;
      return dateA - dateB;
    }
    return 0;
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-5 h-24 animate-pulse" />
        ))}
      </div>
    );
  }

  const title =
    filter === 'today' ? 'Today' :
    filter === 'upcoming' ? 'Upcoming' :
    filter === 'completed' ? 'Completed' :
    pageTitle || 'All Tasks';

  const handleRefresh = () => fetchTasks(true);

  return (
    <div className="space-y-6">
      <Header />

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-2">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{title}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="hover:bg-muted"
            aria-label="Refresh tasks"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
          <AddTaskDialog onTaskAdded={handleTaskAdded} />
        </div>
      </div>

      {/* Search and Filter Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <SearchAndFilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          priorityFilter={priorityFilter}
          onPriorityFilterChange={setPriorityFilter}
          taskCount={filteredTasks.length}
        />
      </motion.div>

      {/* Task List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <TaskList
          tasks={filteredTasks}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
          filter={filter}
        />
      </motion.div>
    </div>
  );
}