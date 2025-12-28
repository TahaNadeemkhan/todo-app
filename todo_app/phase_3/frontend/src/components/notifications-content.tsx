"use client";

import { useState, useEffect } from "react";
import { useSession } from "@/lib/auth-client";
import apiClient from "@/lib/api";
import { Notification } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Header } from "@/components/header";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bell,
  BellOff,
  Check,
  CheckCheck,
  Trash2,
  RefreshCw,
  Mail,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function NotificationsContent() {
  const { data: session } = useSession();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const fetchNotifications = async (showToast = false) => {
    if (!session?.user?.id) return;

    if (showToast) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const params = filter === "unread" ? { unread_only: true } : {};
      const response = await apiClient.get<Notification[]>(
        `/api/${session.user.id}/notifications`,
        { params }
      );
      setNotifications(response.data);
      if (showToast) {
        toast.success("Notifications refreshed");
      }
    } catch (error) {
      console.error("Failed to fetch notifications", error);
      toast.error("Failed to load notifications");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [session?.user?.id, filter]);

  const markAsRead = async (notificationIds: number[]) => {
    if (!session?.user?.id) return;

    try {
      await apiClient.patch(`/api/${session.user.id}/notifications/mark-read`, {
        notification_ids: notificationIds,
      });
      setNotifications((prev) =>
        prev.map((n) =>
          notificationIds.includes(n.id) ? { ...n, is_read: true } : n
        )
      );
      toast.success("Marked as read");
    } catch (error) {
      console.error("Failed to mark as read", error);
      toast.error("Failed to mark as read");
    }
  };

  const markAllAsRead = async () => {
    if (!session?.user?.id) return;

    try {
      await apiClient.patch(`/api/${session.user.id}/notifications/mark-all-read`);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      toast.success("All notifications marked as read");
    } catch (error) {
      console.error("Failed to mark all as read", error);
      toast.error("Failed to mark all as read");
    }
  };

  const deleteNotification = async (notificationId: number) => {
    if (!session?.user?.id) return;

    try {
      await apiClient.delete(
        `/api/${session.user.id}/notifications/${notificationId}`
      );
      setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
      toast.success("Notification deleted");
    } catch (error) {
      console.error("Failed to delete notification", error);
      toast.error("Failed to delete notification");
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "task_created":
        return <Bell className="h-5 w-5 text-blue-500" />;
      case "task_updated":
        return <RefreshCw className="h-5 w-5 text-orange-500" />;
      case "task_completed":
        return <CheckCheck className="h-5 w-5 text-green-500" />;
      case "task_deleted":
        return <Trash2 className="h-5 w-5 text-red-500" />;
      case "due_reminder":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Mail className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="space-y-6">
      <Header />

      <div className="max-w-4xl mx-auto">
        {/* Page Title and Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-2 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Notifications</h1>
            <p className="text-sm text-muted-foreground mt-1">
              {unreadCount > 0
                ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? "s" : ""}`
                : "All caught up!"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => fetchNotifications(true)}
              disabled={isRefreshing}
              className="hover:bg-muted"
              aria-label="Refresh notifications"
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
            {unreadCount > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={markAllAsRead}
                className="gap-2"
              >
                <CheckCheck className="h-4 w-4" />
                Mark all read
              </Button>
            )}
          </div>
        </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={filter === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("all")}
        >
          All
        </Button>
        <Button
          variant={filter === "unread" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("unread")}
        >
          Unread {unreadCount > 0 && `(${unreadCount})`}
        </Button>
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : notifications.length === 0 ? (
        <Card className="p-12 text-center">
          <BellOff className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
          <h3 className="font-medium text-foreground mb-1">No notifications</h3>
          <p className="text-sm text-muted-foreground">
            {filter === "unread"
              ? "You've read all your notifications"
              : "You don't have any notifications yet"}
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {notifications.map((notification) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.2 }}
              >
                <Card
                  className={cn(
                    "p-4 transition-all hover:shadow-md",
                    !notification.is_read &&
                      "border-l-4 border-l-blue-500 bg-blue-50/50 dark:bg-blue-950/20"
                  )}
                >
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h3
                            className={cn(
                              "font-medium text-foreground",
                              !notification.is_read && "font-semibold"
                            )}
                          >
                            {notification.title}
                          </h3>
                          <p className="text-sm text-muted-foreground mt-1">
                            {notification.message}
                          </p>
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {formatDate(notification.sent_at)}
                        </span>
                      </div>

                      {/* Email sent indicator */}
                      <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                        <Mail className="h-3 w-3" />
                        <span>Sent to {notification.email_sent_to}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 flex-shrink-0">
                      {!notification.is_read && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => markAsRead([notification.id])}
                          title="Mark as read"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
                        onClick={() => deleteNotification(notification.id)}
                        title="Delete notification"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
      </div>
    </div>
  );
}
