"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Bell, Mail, Smartphone } from "lucide-react";
import { motion } from "framer-motion";

export interface ReminderOption {
  remind_before: string; // ISO duration
  channels: string[];
}

interface ReminderConfigProps {
  reminders: ReminderOption[];
  onChange: (reminders: ReminderOption[]) => void;
  disabled?: boolean;
}

export function ReminderConfig({
  reminders,
  onChange,
  disabled,
}: ReminderConfigProps) {
  const [remindBefore, setRemindBefore] = useState("PT1H"); // Default 1 hour
  const [channels, setChannels] = useState<string[]>(["email"]);

  const handleAddReminder = () => {
    // Only add if not already exists with same timing
    if (!reminders.some(r => r.remind_before === remindBefore)) {
      onChange([...reminders, { remind_before: remindBefore, channels }]);
    }
  };

  const handleRemoveReminder = (index: number) => {
    onChange(reminders.filter((_, i) => i !== index));
  };

  const timingOptions = [
    { label: "At time of event", value: "PT0S" },
    { label: "15 minutes before", value: "PT15M" },
    { label: "1 hour before", value: "PT1H" },
    { label: "1 day before", value: "P1D" },
    { label: "1 week before", value: "P1W" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm font-medium text-foreground">
        <Bell className="h-4 w-4" />
        <span>Reminders</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {reminders.map((reminder, idx) => (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            key={idx}
            className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-3 py-1 text-xs"
          >
            <span>{timingOptions.find(o => o.value === reminder.remind_before)?.label || reminder.remind_before}</span>
            <div className="flex gap-1 border-l border-primary/20 pl-2">
              {reminder.channels.includes("email") && <Mail className="h-3 w-3" />}
              {reminder.channels.includes("push") && <Smartphone className="h-3 w-3" />}
            </div>
            <button
              type="button"
              onClick={() => handleRemoveReminder(idx)}
              className="ml-1 text-muted-foreground hover:text-destructive transition-colors"
            >
              ×
            </button>
          </motion.div>
        ))}
      </div>

      <div className="flex items-end gap-2">
        <div className="grid gap-2 flex-1">
          <Label className="text-[10px] uppercase text-muted-foreground">Timing</Label>
          <Select
            value={remindBefore}
            onValueChange={setRemindBefore}
            disabled={disabled}
          >
            <SelectTrigger className="h-9 bg-white/50 border-white/20">
              <SelectValue placeholder="Select timing" />
            </SelectTrigger>
            <SelectContent>
              {timingOptions.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-2 justify-center pb-2">
          <div className="flex items-center gap-2">
            <Checkbox
              id="push-channel"
              checked={channels.includes("push")}
              onCheckedChange={(checked) => {
                if (checked) setChannels([...channels, "push"]);
                else setChannels(channels.filter(c => c !== "push"));
              }}
              disabled={disabled}
            />
            <Label htmlFor="push-channel" className="text-xs font-normal">Push</Label>
          </div>
          <div className="flex items-center gap-2">
            <Checkbox
              id="email-channel"
              checked={channels.includes("email")}
              onCheckedChange={(checked) => {
                if (checked) setChannels([...channels, "email"]);
                else setChannels(channels.filter(c => c !== "email"));
              }}
              disabled={disabled}
            />
            <Label htmlFor="email-channel" className="text-xs font-normal">Email</Label>
          </div>
        </div>

        <button
          type="button"
          onClick={handleAddReminder}
          disabled={disabled || channels.length === 0}
          className="h-9 px-3 bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded-md text-xs font-medium transition-colors disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>
  );
}
