"use client";

import { useRouter } from "next/navigation";
import { signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { LogOut } from "lucide-react";

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await signOut();
      toast.success("Logged out successfully");
      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Failed to log out");
    }
  };

  return (
    <Button 
      variant="ghost" 
      size="icon"
      onClick={handleLogout}
      className="rounded-full hover:bg-destructive/10 hover:text-destructive transition-colors"
      title="Log out"
    >
      <LogOut className="h-4 w-4" />
    </Button>
  );
}