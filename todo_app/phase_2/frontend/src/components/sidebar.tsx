"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import { LogoutButton } from "@/components/logout-button";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Calendar,
  CalendarClock,
  CheckCircle2,
  Settings,
  User,
  Sun,
  Bell,
} from "lucide-react";

export function Sidebar() {
  const { data: session } = useSession();
  const pathname = usePathname();

  const links = [
    { href: "/dashboard", label: "All Tasks", icon: LayoutDashboard },
    { href: "/today", label: "Today", icon: Sun },
    { href: "/upcoming", label: "Upcoming", icon: CalendarClock },
    { href: "/completed", label: "Completed", icon: CheckCircle2 },
    { href: "/notifications", label: "Notifications", icon: Bell },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-background border-r border-border flex flex-col">
      {/* Logo */}
      <div className="h-14 px-4 flex items-center border-b border-border">
        <Link href="/" className="flex items-center gap-2 hover:opacity-70 transition-opacity">
          <div className="h-7 w-7 rounded-lg bg-blue-600 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-base text-foreground">iTasks</span>
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.label}
              href={link.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400"
                  : "text-foreground/70 hover:bg-muted hover:text-foreground"
              )}
            >
              <link.icon className="w-5 h-5 flex-shrink-0" />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section: Settings, User, Theme */}
      <div className="border-t border-border">
        {/* Settings Link */}
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors",
            pathname === "/settings"
              ? "bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400"
              : "text-foreground/70 hover:bg-muted hover:text-foreground"
          )}
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </Link>

        {/* User Info & Controls */}
        <div className="px-3 py-3 space-y-3">
          {/* Theme Toggle */}
          <div className="flex items-center justify-between px-3">
            <span className="text-xs font-medium text-muted-foreground">Theme</span>
            <ThemeToggle />
          </div>

          {/* User Profile */}
          {session && (
            <div className="px-3 py-2 rounded-lg bg-muted/50 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-blue-700 dark:text-blue-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-foreground truncate">
                    {session.user.name}
                  </p>
                  <p className="text-[10px] text-muted-foreground truncate">
                    {session.user.email}
                  </p>
                </div>
              </div>
              <LogoutButton />
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
