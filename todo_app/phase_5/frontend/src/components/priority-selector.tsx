"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type Priority = "low" | "medium" | "high";

interface PrioritySelectorProps {
  value: Priority;
  onChange: (value: Priority) => void;
  className?: string;
}

export function PrioritySelector({ value, onChange, className }: PrioritySelectorProps) {
  const getPriorityColor = (p: Priority) => {
    switch (p) {
      case "high":
        return "text-red-500 bg-red-500/10 hover:bg-red-500/20 border-red-500/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 hover:bg-yellow-500/20 border-yellow-500/20";
      case "low":
        return "text-green-500 bg-green-500/10 hover:bg-green-500/20 border-green-500/20";
      default:
        return "text-muted-foreground bg-muted hover:bg-muted/80";
    }
  };

  return (
    <Select value={value} onValueChange={(v) => onChange(v as Priority)}>
      <SelectTrigger className={cn("w-[120px] h-8", getPriorityColor(value), className)}>
        <SelectValue placeholder="Priority" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="low" className="text-green-500 focus:text-green-500">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            Low
          </div>
        </SelectItem>
        <SelectItem value="medium" className="text-yellow-500 focus:text-yellow-500">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-yellow-500" />
            Medium
          </div>
        </SelectItem>
        <SelectItem value="high" className="text-red-500 focus:text-red-500">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-500" />
            High
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}
