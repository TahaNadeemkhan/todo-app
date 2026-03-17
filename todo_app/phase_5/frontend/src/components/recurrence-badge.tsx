import { Badge } from "@/components/ui/badge";
import { RecurrenceConfig } from "./recurrence-config-dialog";

interface RecurrenceBadgeProps {
  recurrence: RecurrenceConfig;
  className?: string;
}

export function RecurrenceBadge({ recurrence, className }: RecurrenceBadgeProps) {
  const getText = () => {
    const { pattern, interval } = recurrence;
    
    switch (pattern) {
      case "daily":
        return `${interval === 1 ? "Daily" : `Every ${interval} days`}`;
      case "weekly":
        return `${interval === 1 ? "Weekly" : `Every ${interval} weeks`} on ${getDaysOfWeekText(recurrence.days_of_week || [])}`;
      case "monthly":
        return `${interval === 1 ? "Monthly" : `Every ${interval} months`} on day ${recurrence.day_of_month}`;
      default:
        return "Recurring";
    }
  };

  const getDaysOfWeekText = (days: number[]) => {
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    if (days.length === 0) return "";
    if (days.length === 7) return "every day";
    return days.map(day => dayNames[day]).join(", ");
  };

  return (
    <Badge variant="secondary" className={className}>
      {getText()}
    </Badge>
  );
}