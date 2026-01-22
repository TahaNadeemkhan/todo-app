import React from "react";
import { cn } from "@/lib/utils";

interface TagBadgeProps {
  name: string;
  color?: string;
  className?: string;
}

export function TagBadge({ name, color, className }: TagBadgeProps) {
  // Default color if none provided
  const backgroundColor = color || "rgba(59, 130, 246, 0.1)"; // Blue-500 with opacity
  const textColor = color || "rgb(59, 130, 246)"; // Blue-500

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium border border-transparent transition-colors",
        className
      )}
      style={{
        backgroundColor: color ? `${color}20` : backgroundColor,
        color: textColor,
        borderColor: color ? `${color}40` : "transparent",
      }}
    >
      #{name}
    </span>
  );
}
