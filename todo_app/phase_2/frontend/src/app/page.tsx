"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { useSession, signOut } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowRight, CheckCircle, Zap, Shield, Layout, LogIn, LogOut } from "lucide-react";

export default function LandingPage() {
  const { data: session, isPending: isLoading } = useSession();
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
    <div className="min-h-screen flex flex-col bg-background">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-card shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-blue-600 flex items-center justify-center">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-foreground">
              iTasks
            </span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {isLoading ? (
              <div className="h-9 w-24 bg-muted animate-pulse rounded" />
            ) : session ? (
              <>
                <span className="text-sm font-medium text-muted-foreground hidden sm:block">
                  {session.user.name || session.user.email}
                </span>
                <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md shadow-blue-500/20 transition-all">
                  <Link href="/dashboard">
                    Dashboard <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  className="hover:bg-destructive/10 hover:text-destructive transition-colors"
                  title="Log out"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" asChild className="hidden sm:inline-flex text-foreground">
                  <Link href="/login" className="flex items-center gap-2">
                    <LogIn className="w-4 h-4" /> Sign In
                  </Link>
                </Button>
                <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md shadow-blue-500/20 transition-all">
                  <Link href="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative pt-16 pb-24 bg-gradient-to-b from-blue-50/50 via-purple-50/30 to-white dark:from-blue-950/20 dark:via-purple-950/10 dark:to-background">
          <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
            <div>
              <span className="inline-block py-1 px-3 rounded-full bg-blue-100 dark:bg-blue-950 text-primary text-sm font-medium mb-6">
                v2.0 Now Available
              </span>
              <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 leading-tight text-foreground">
                Organize your life
                <br />
                with elegance.
              </h1>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
                The most beautiful and intuitive task manager you've ever used.
                Designed for focus, built for speed.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
                <Button size="lg" asChild className="h-12 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg shadow-blue-500/30 transition-all">
                  <Link href="/register">Start for free <ArrowRight className="ml-2 h-4 w-4" /></Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="h-12 px-8 border-blue-200 hover:bg-blue-50 dark:border-blue-900 dark:hover:bg-blue-950/50 transition-all">
                  <Link href="https://github.com/TahaNadeemkhan/todo-app" target="_blank">View on GitHub</Link>
                </Button>
              </div>
            </div>

            {/* Hero Image / Mockup */}
            <div className="relative w-full max-w-5xl rounded-2xl overflow-hidden shadow-2xl border border-border/50">
              {/* MacBook Style Frame */}
              <div className="bg-zinc-800 dark:bg-zinc-900 rounded-t-2xl">
                {/* Browser Header */}
                <div className="h-10 flex items-center px-4 gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                  </div>
                  <div className="flex-1 mx-4">
                    <div className="bg-zinc-700 dark:bg-zinc-800 rounded-md h-6 flex items-center justify-center">
                      <span className="text-xs text-zinc-400">https://itask-chi.vercel.app/dashboard</span>
                    </div>
                  </div>
                </div>
              </div>
              {/* Dashboard Screenshot */}
              <div className="relative w-full">
                <Image
                  src="/images/dashboard-preview.png"
                  alt="iTasks Dashboard Preview"
                  width={1397}
                  height={911}
                  className="w-full h-auto"
                  priority
                />
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20 border-t border-border">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-3 text-foreground">Everything you need</h2>
              <p className="text-muted-foreground">Powerful features wrapped in a clean interface.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: Zap,
                  title: "Lightning Fast",
                  desc: "Built with Next.js 15 and FastAPI for instant interactions."
                },
                {
                  icon: Shield,
                  title: "Secure by Default",
                  desc: "Enterprise-grade auth with Better Auth and PostgreSQL."
                },
                {
                  icon: Layout,
                  title: "Beautiful Design",
                  desc: "Clean, minimal design that makes work feel like play."
                }
              ].map((feature, i) => (
                <div
                  key={i}
                  className="p-6 border border-border rounded-lg bg-card hover:shadow-md transition-shadow"
                >
                  <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-4">
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-foreground">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm">
                    {feature.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 bg-card">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-blue-600 flex items-center justify-center">
              <CheckCircle className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-semibold text-foreground">iTasks</span>
          </div>
          <div className="text-sm text-muted-foreground">
            © 2025 Todo App. Open Source.
          </div>
          <div className="flex gap-6">
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">Terms</Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">Privacy</Link>
            <Link href="https://github.com/TahaNadeemkhan/todo-app" className="text-sm text-muted-foreground hover:text-foreground">GitHub</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
