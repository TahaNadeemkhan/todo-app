"use client";

import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Calendar as CalendarIcon, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface DueDateTimePickerProps {
  date: string;
  time: string;
  onDateChange: (date: string) => void;
  onTimeChange: (time: string) => void;
  className?: string;
}

export function DueDateTimePicker({
  date,
  time,
  onDateChange,
  onTimeChange,
  className,
}: DueDateTimePickerProps) {
  return (
    <div className={cn("grid grid-cols-2 gap-4", className)}>
      <div className="grid gap-2">
        <Label htmlFor="dueDate" className="flex items-center gap-2">
          <CalendarIcon className="h-3.5 w-3.5" />
          Due Date
        </Label>
        <Input
          id="dueDate"
          type="date"
          value={date}
          onChange={(e) => onDateChange(e.target.value)}
          className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="dueTime" className="flex items-center gap-2">
          <Clock className="h-3.5 w-3.5" />
          Due Time <span className="text-[10px] text-muted-foreground">(Optional)</span>
        </Label>
        <Input
          id="dueTime"
          type="time"
          value={time}
          onChange={(e) => onTimeChange(e.target.value)}
          disabled={!date}
          className="bg-white/50 border-white/20 focus:border-primary/50 transition-all disabled:opacity-50"
        />
      </div>
    </div>
  );
}
