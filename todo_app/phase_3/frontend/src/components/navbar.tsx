"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import { LogoutButton } from "@/components/logout-button";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Calendar, CheckSquare, Settings, Menu, X, LogIn } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

export function Navbar() {
  const { data: session, isPending: isLoading } = useSession();
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/today", label: "Today", icon: Calendar }, 
    { href: "/upcoming", label: "Upcoming", icon: CheckSquare },
    { href: "/completed", label: "Completed", icon: CheckSquare },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-white/30 dark:bg-black/30 backdrop-blur-2xl shadow-sm transition-all">
      <div className="max-w-5xl mx-auto px-6 h-16 flex justify-between items-center">
        {/* Left side: Logo and Desktop Navigation */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-purple-500 shadow-lg shadow-primary/20" />
            <span className="font-bold tracking-tight hidden sm:block">iTasks</span>
          </Link>

          <nav className="hidden md:flex gap-1">
            {links.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.label}
                  href={link.href}
                  className={cn(
                    "px-3 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2",
                    isActive 
                      ? "bg-white/10 text-foreground shadow-sm ring-1 ring-white/10" 
                      : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                  )}
                >
                  <link.icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right side: Theme Toggle, User Info, Auth/Logout Button, Mobile Toggle */}
        <div className="flex items-center gap-2">
          <ThemeToggle />

          {isLoading ? (
            <div className="h-9 w-24 bg-muted/20 animate-pulse rounded-full" />
          ) : session ? (
            <>
              <span className="text-sm font-medium text-muted-foreground hidden sm:block bg-white/10 px-3 py-1 rounded-full border border-white/5">
                {session.user.name}
              </span>
              <LogoutButton />
            </>
          ) : (
            <Button
              asChild
              className="rounded-full shadow-lg hover:shadow-primary/25 bg-gradient-to-r from-primary to-purple-600 border-0 transition-all duration-300"
            >
              <Link href="/login" className="flex items-center gap-2">
                <LogIn className="w-4 h-4" /> Sign In
              </Link>
            </Button>
          )}

          {/* Mobile menu toggle button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/10 bg-white/30 dark:bg-black/30 backdrop-blur-2xl overflow-hidden absolute w-full"
          >
            <nav className="p-4 flex flex-col gap-2">
              {links.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="px-4 py-3 rounded-lg text-base font-medium hover:bg-white/10 flex items-center gap-3 transition-colors text-foreground"
                >
                  <link.icon className="w-5 h-5" />
                  {link.label}
                </Link>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}