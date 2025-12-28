"use client";

import { Menu, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSidebar } from "@/lib/sidebar-context";
import { useState } from "react";

interface HeaderProps {
  onRefresh?: () => Promise<void> | void;
  title?: string;
}

export function Header({ onRefresh, title }: HeaderProps) {
  const { toggle } = useSidebar();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (!onRefresh) return;

    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <header className="h-14 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-30">
      <div className="h-full px-4 flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggle}
          className="hover:bg-muted"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>

        {title && (
          <h1 className="text-lg font-semibold text-foreground">{title}</h1>
        )}

        <div className="ml-auto flex items-center gap-2">
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="hover:bg-muted"
              aria-label="Refresh tasks"
            >
              <RefreshCw className={`h-5 w-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
