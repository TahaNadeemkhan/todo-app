"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { Task } from "@/lib/types";
import { TaskList } from "@/components/task-list";
import { AddTaskDialog } from "@/components/add-task-dialog";
import { SearchAndFilterBar } from "@/components/search-and-filter-bar";
import { SortSelector, SortBy, SortOrder } from "@/components/sort-selector";
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
  const [tagsFilter, setTagsFilter] = useState("");

  // Sort state
  const [sortBy, setSortBy] = useState<SortBy>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const filter = forcedFilter || searchParams.get("filter");

  // Load sort preference from localStorage
  useEffect(() => {
    const savedSort = localStorage.getItem("taskSortPreference");
    if (savedSort) {
      try {
        const { by, order } = JSON.parse(savedSort);
        setSortBy(by);
        setSortOrder(order);
      } catch (e) {
        console.error("Failed to parse sort preference", e);
      }
    }
  }, []);

  const handleSortChange = (by: SortBy, order: SortOrder) => {
    setSortBy(by);
    setSortOrder(order);
    localStorage.setItem("taskSortPreference", JSON.stringify({ by, order }));
  };

  useEffect(() => {
    if (session?.user?.id) {
      // Debounce search query to avoid too many requests
      const timeoutId = setTimeout(() => {
        fetchTasks();
      }, 300);
      return () => clearTimeout(timeoutId);
    }
  }, [session?.user?.id, searchQuery, statusFilter, priorityFilter, tagsFilter, sortBy, sortOrder, filter]);

  const fetchTasks = async (showToast = false) => {
    if (showToast) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const params = new URLSearchParams();
      
      // Search and Basic Filters
      if (searchQuery) params.append("search", searchQuery);
      if (priorityFilter !== "all") params.append("priority", priorityFilter);
      if (tagsFilter) params.append("tags", tagsFilter);
      
      // Status Filter
      if (statusFilter === "completed") params.append("completed", "true");
      if (statusFilter === "incomplete") params.append("completed", "false");

      // Sorting
      params.append("sort_by", sortBy);
      params.append("sort_order", sortOrder);

      // View-based Filters (Today, Upcoming)
      if (filter === "completed") params.append("completed", "true");

      const response = await apiClient.get<Task[]>(`/api/${session?.user?.id}/tasks?${params.toString()}`);
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
    // Re-fetch to ensure sort order/filters
    fetchTasks(); 
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
  };

  const handleTaskDeleted = (taskId: string) => {
    setTasks(tasks.filter((t) => t.id !== taskId));
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setStatusFilter("all");
    setPriorityFilter("all");
    setTagsFilter("");
  };

  // Apply client-side date filtering for "Today" and "Upcoming" views
  const filteredTasks = tasks.filter((task) => {
    if (filter === "today") {
      if (!task.due_date) return false;
      const taskDate = new Date(task.due_date);
      const today = new Date();
      return taskDate.setHours(0,0,0,0) === today.setHours(0,0,0,0);
    }
    if (filter === "upcoming") {
      if (!task.due_date) return false;
      const taskDate = new Date(task.due_date);
      const today = new Date();
      return taskDate.setHours(0,0,0,0) > today.setHours(0,0,0,0);
    }
    return true;
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

      {/* Search, Filter, and Sort Controls */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="flex flex-col gap-4"
      >
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-end">
          <div className="flex-1 w-full">
            <SearchAndFilterBar
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              statusFilter={statusFilter}
              onStatusFilterChange={setStatusFilter}
              priorityFilter={priorityFilter}
              onPriorityFilterChange={setPriorityFilter}
              tagsFilter={tagsFilter}
              onTagsFilterChange={setTagsFilter}
              onClear={handleClearFilters}
              taskCount={filteredTasks.length}
            />
          </div>
          <div className="pb-8">
            <SortSelector 
              sortBy={sortBy} 
              sortOrder={sortOrder} 
              onSortChange={handleSortChange} 
            />
          </div>
        </div>
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