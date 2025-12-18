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
    <div className="space-y-4 mb-8">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-11 h-11 bg-card border-border
                     text-foreground
                     focus:ring-2 focus:ring-primary/20 transition-all
                     placeholder:text-muted-foreground"
        />
      </div>

      {/* Filter Controls */}
      <div className="flex flex-wrap gap-3 items-center">
        <span className="text-sm font-medium text-muted-foreground">
          Filter:
        </span>

        {/* Status Filter */}
        <Select
          value={statusFilter}
          onValueChange={onStatusFilterChange}
        >
          <SelectTrigger className="w-[140px] h-9 bg-card border-border text-foreground">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            <SelectItem value="all" className="text-foreground">All Tasks</SelectItem>
            <SelectItem value="incomplete" className="text-foreground">Incomplete</SelectItem>
            <SelectItem value="completed" className="text-foreground">Completed</SelectItem>
          </SelectContent>
        </Select>

        {/* Priority Filter */}
        <Select
          value={priorityFilter}
          onValueChange={onPriorityFilterChange}
        >
          <SelectTrigger className="w-[140px] h-9 bg-card border-border text-foreground">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            <SelectItem value="all" className="text-foreground">All Priorities</SelectItem>
            <SelectItem value="high" className="text-foreground">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                High
              </span>
            </SelectItem>
            <SelectItem value="medium" className="text-foreground">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-yellow-500" />
                Medium
              </span>
            </SelectItem>
            <SelectItem value="low" className="text-foreground">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                Low
              </span>
            </SelectItem>
          </SelectContent>
        </Select>

        {/* Result Count */}
        {taskCount > 0 && (
          <div className="text-sm font-medium text-muted-foreground ml-auto">
            {taskCount} {taskCount === 1 ? "task" : "tasks"}
          </div>
        )}
      </div>
    </div>
  );
}
