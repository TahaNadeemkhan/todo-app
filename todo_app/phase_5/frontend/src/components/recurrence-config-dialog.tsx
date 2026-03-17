import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

export interface RecurrenceConfig {
  pattern: "daily" | "weekly" | "monthly";
  interval: number;
  days_of_week?: number[]; // 0 = Sunday, 1 = Monday, etc.
  day_of_month?: number; // 1-31
}

interface RecurrenceConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (config: RecurrenceConfig) => void;
  initialConfig?: RecurrenceConfig | null;
}

export function RecurrenceConfigDialog({
  open,
  onOpenChange,
  onSave,
  initialConfig,
}: RecurrenceConfigDialogProps) {
  const [pattern, setPattern] = useState<RecurrenceConfig["pattern"]>(
    initialConfig?.pattern || "daily"
  );
  const [interval, setInterval] = useState(initialConfig?.interval?.toString() || "1");
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(
    initialConfig?.days_of_week || []
  );
  const [dayOfMonth, setDayOfMonth] = useState(
    initialConfig?.day_of_month?.toString() || ""
  );

  const handleSave = () => {
    const config: RecurrenceConfig = {
      pattern,
      interval: parseInt(interval),
    };

    if (pattern === "weekly") {
      config.days_of_week = daysOfWeek;
    } else if (pattern === "monthly") {
      config.day_of_month = parseInt(dayOfMonth);
    }

    onSave(config);
    onOpenChange(false);
  };

  const handleDayToggle = (day: number) => {
    setDaysOfWeek(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-card border-border">
        <DialogHeader>
          <DialogTitle>Recurrence Settings</DialogTitle>
          <DialogDescription>
            Configure how often this task repeats.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Pattern</Label>
            <RadioGroup
              value={pattern}
              onValueChange={(v) => setPattern(v as RecurrenceConfig["pattern"])}
              className="grid grid-cols-3 gap-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="daily" id="daily" />
                <Label htmlFor="daily">Daily</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="weekly" id="weekly" />
                <Label htmlFor="weekly">Weekly</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="monthly" id="monthly" />
                <Label htmlFor="monthly">Monthly</Label>
              </div>
            </RadioGroup>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="interval">Every</Label>
            <div className="flex items-center gap-2">
              <Input
                id="interval"
                type="number"
                min="1"
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
                className="bg-white/50 border-white/20 focus:border-primary/50 transition-all"
              />
              <span className="text-sm text-muted-foreground">
                {pattern === "daily" && "day(s)"}
                {pattern === "weekly" && "week(s)"}
                {pattern === "monthly" && "month(s)"}
              </span>
            </div>
          </div>

          {pattern === "weekly" && (
            <div className="grid gap-2">
              <Label>Days of Week</Label>
              <div className="grid grid-cols-7 gap-2">
                {["S", "M", "T", "W", "T", "F", "S"].map((day, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleDayToggle(index)}
                    className={`py-2 rounded flex items-center justify-center text-sm ${
                      daysOfWeek.includes(index)
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                    }`}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>
          )}

          {pattern === "monthly" && (
            <div className="grid gap-2">
              <Label htmlFor="dayOfMonth">Day of Month</Label>
              <Select
                value={dayOfMonth}
                onValueChange={setDayOfMonth}
              >
                <SelectTrigger className="bg-white/50 border-white/20 focus:border-primary/50 transition-all">
                  <SelectValue placeholder="Select day" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 31 }, (_, i) => i + 1).map(day => (
                    <SelectItem key={day} value={day.toString()}>
                      {day}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}