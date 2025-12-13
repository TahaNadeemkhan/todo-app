"use client";

import { useSession } from "@/lib/auth-client";
import { LogoutButton } from "@/components/logout-button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

export default function SettingsPage() {
  const { data: session } = useSession();

  return (
    <div>
        <h1 className="text-3xl font-bold mb-8 tracking-tight">Settings</h1>
        
        <Card className="glass-panel border-white/20">
            <CardHeader>
                <CardTitle>Account</CardTitle>
                <CardDescription>Manage your account settings.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="grid gap-2">
                    <Label>Name</Label>
                    <div className="px-3 py-2 rounded-md bg-white/5 border border-white/10 text-sm font-medium">
                        {session?.user?.name}
                    </div>
                </div>
                <div className="grid gap-2">
                    <Label>Email</Label>
                    <div className="px-3 py-2 rounded-md bg-white/5 border border-white/10 text-sm font-medium">
                        {session?.user?.email}
                    </div>
                </div>
                
                <div className="pt-4 border-t border-white/10">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium text-sm">Sign Out</p>
                            <p className="text-xs text-muted-foreground">Sign out of your account on this device.</p>
                        </div>
                        <LogoutButton />
                    </div>
                </div>
            </CardContent>
        </Card>
    </div>
  )
}
