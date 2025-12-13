"use client";

import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SearchAndFilterBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: "all" | "completed" | "incomplete";
  onStatusFilterChange: (status: "all" | "completed" | "incomplete") => void;
  priorityFilter: "all" | "high" | "medium" | "low";
  onPriorityFilterChange: (priority: "all" | "high" | "medium" | "low") => void;
  taskCount?: number;
}

export function SearchAndFilterBar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  priorityFilter,
  onPriorityFilterChange,
  taskCount = 0,
}: SearchAndFilterBarProps) {
  return (
    <div className="space-y-4 mb-6">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search tasks by title or description..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 h-12 bg-card/50 backdrop-blur-sm border-border/50
                     focus:ring-2 focus:ring-primary/20 transition-all
                     placeholder:text-muted-foreground/60"
        />
      </div>

      {/* Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium text-muted-foreground">
            Filters:
          </span>
        </div>

        <div className="flex flex-wrap gap-3 flex-1">
          {/* Status Filter */}
          <div className="flex-1 min-w-[140px]">
            <Select
              value={statusFilter}
              onValueChange={onStatusFilterChange}
            >
              <SelectTrigger className="h-10 bg-card/50 backdrop-blur-sm border-border/50">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tasks</SelectItem>
                <SelectItem value="incomplete">Incomplete</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Priority Filter */}
          <div className="flex-1 min-w-[140px]">
            <Select
              value={priorityFilter}
              onValueChange={onPriorityFilterChange}
            >
              <SelectTrigger className="h-10 bg-card/50 backdrop-blur-sm border-border/50">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="high">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    High
                  </span>
                </SelectItem>
                <SelectItem value="medium">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-yellow-500" />
                    Medium
                  </span>
                </SelectItem>
                <SelectItem value="low">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                    Low
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Result Count */}
        {taskCount > 0 && (
          <div className="text-sm text-muted-foreground whitespace-nowrap">
            {taskCount} {taskCount === 1 ? "task" : "tasks"}
          </div>
        )}
      </div>
    </div>
  );
}
