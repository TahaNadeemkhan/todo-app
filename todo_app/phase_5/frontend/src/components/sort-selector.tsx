"use client";

import { ArrowDownAZ, ArrowDownZA, Calendar, Clock, ArrowUp, ArrowDown } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export type SortBy = "due_at" | "priority" | "created_at" | "title";
export type SortOrder = "asc" | "desc";

interface SortSelectorProps {
  sortBy: SortBy;
  sortOrder: SortOrder;
  onSortChange: (by: SortBy, order: SortOrder) => void;
}

export function SortSelector({ sortBy, sortOrder, onSortChange }: SortSelectorProps) {
  const handleValueChange = (value: string) => {
    const [by, order] = value.split("-") as [SortBy, SortOrder];
    onSortChange(by, order);
  };

  const value = `${sortBy}-${sortOrder}`;

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-muted-foreground">Sort by:</span>
      <Select value={value} onValueChange={handleValueChange}>
        <SelectTrigger className="w-[180px] h-9 bg-card border-border text-foreground">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent className="bg-card border-border">
          <SelectItem value="due_at-asc" className="text-foreground">
            <span className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Due Date (Soonest)
            </span>
          </SelectItem>
          <SelectItem value="due_at-desc" className="text-foreground">
            <span className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Due Date (Latest)
            </span>
          </SelectItem>
          <SelectItem value="priority-asc" className="text-foreground">
            <span className="flex items-center gap-2">
              <ArrowUp className="h-4 w-4" />
              Priority (High to Low)
            </span>
          </SelectItem>
          <SelectItem value="priority-desc" className="text-foreground">
            <span className="flex items-center gap-2">
              <ArrowDown className="h-4 w-4" />
              Priority (Low to High)
            </span>
          </SelectItem>
          <SelectItem value="created_at-desc" className="text-foreground">
            <span className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Created (Newest)
            </span>
          </SelectItem>
          <SelectItem value="created_at-asc" className="text-foreground">
            <span className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Created (Oldest)
            </span>
          </SelectItem>
          <SelectItem value="title-asc" className="text-foreground">
            <span className="flex items-center gap-2">
              <ArrowDownAZ className="h-4 w-4" />
              Title (A-Z)
            </span>
          </SelectItem>
          <SelectItem value="title-desc" className="text-foreground">
            <span className="flex items-center gap-2">
              <ArrowDownZA className="h-4 w-4" />
              Title (Z-A)
            </span>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
