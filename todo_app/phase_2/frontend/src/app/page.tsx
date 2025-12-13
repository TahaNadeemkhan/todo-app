"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { useSession } from "@/lib/auth-client";
import { ArrowRight, CheckCircle, Zap, Shield, Layout } from "lucide-react";
import { motion } from "framer-motion";

export default function LandingPage() {
  const { data: session, isLoading } = useSession();

  return (
    <div className="min-h-screen flex flex-col overflow-hidden relative">
      {/* Background Elements */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/10 blur-3xl animate-float" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/10 blur-3xl animate-float" style={{ animationDelay: "2s" }} />
      </div>

      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-white/30 dark:bg-black/30 backdrop-blur-xl shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-purple-500 shadow-lg shadow-primary/20" />
            <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
              iTasks
            </span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {isLoading ? (
              <div className="h-9 w-24 bg-muted/20 animate-pulse rounded-full" />
            ) : session ? (
              <Button asChild className="rounded-full shadow-lg hover:shadow-primary/25 bg-gradient-to-r from-primary to-purple-600 border-0">
                <Link href="/dashboard">
                  Dashboard <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            ) : (
              <>
                <Button variant="ghost" asChild className="hidden sm:inline-flex rounded-full hover:bg-white/10">
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild className="rounded-full shadow-lg hover:shadow-primary/25 bg-gradient-to-r from-primary to-purple-600 border-0">
                  <Link href="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative pt-20 pb-32 overflow-hidden">
          <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="inline-block py-1 px-3 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 border border-primary/20">
                v2.0 Now Available
              </span>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight overflow-visible">
                <span className="bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/50">
                  Organize your life
                </span>
                <br />
                <span className="bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/50">
                  with elegance.
                </span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
                The most beautiful and intuitive task manager you've ever used. 
                Designed for focus, built for speed, and styled for the future.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
                <Button size="lg" asChild className="rounded-full h-12 px-8 text-base shadow-xl hover:shadow-primary/25 bg-gradient-to-r from-primary to-purple-600 border-0 hover:scale-105 transition-all">
                  <Link href="/register">Start for free <ArrowRight className="ml-2 h-4 w-4" /></Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="rounded-full h-12 px-8 text-base backdrop-blur-md bg-white/10 border-white/20 hover:bg-white/20">
                  <Link href="https://github.com/TahaNadeemkhan/todo-app" target="_blank">View on GitHub</Link>
                </Button>
              </div>
            </motion.div>

            {/* Hero Image / Mockup */}
            <motion.div
              initial={{ opacity: 0, y: 40, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative w-full max-w-5xl aspect-[16/9] rounded-2xl overflow-hidden shadow-2xl border border-white/20 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm group"
            >
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 via-purple-500/10 to-pink-500/10" />

              {/* Mock Interface - Professional Dashboard Preview */}
              <div className="absolute inset-4 rounded-xl bg-background/95 backdrop-blur-2xl border border-white/20 overflow-hidden flex flex-col shadow-inner">
                {/* Mock Header */}
                <div className="h-14 border-b border-border flex items-center px-6 gap-4 bg-card/50">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/70" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                    <div className="w-3 h-3 rounded-full bg-green-500/70" />
                  </div>
                  <div className="text-xs font-medium text-foreground/80">iTasks Dashboard</div>
                </div>
                {/* Mock Content - Realistic Tasks */}
                <div className="flex-1 p-6 md:p-8 grid gap-3 bg-gradient-to-br from-background to-background/50">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-lg font-semibold text-foreground">Today</div>
                    <div className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">3 tasks</div>
                  </div>

                  {/* Task Items */}
                  {[
                    { done: true, text: "Review pull requests", priority: "high" },
                    { done: false, text: "Update project documentation", priority: "medium" },
                    { done: false, text: "Team standup at 10:00 AM", priority: "high" }
                  ].map((task, i) => (
                    <div key={i} className="h-14 md:h-16 rounded-lg border border-border bg-card/80 backdrop-blur-sm flex items-center px-4 gap-3 shadow-sm hover:shadow-md transition-shadow">
                      <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${task.done ? 'bg-primary border-primary' : 'border-muted-foreground/30'}`}>
                        {task.done && <CheckCircle className="w-3 h-3 text-primary-foreground" />}
                      </div>
                      <div className={`flex-1 text-sm font-medium ${task.done ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                        {task.text}
                      </div>
                      <div className={`hidden sm:block px-2 py-0.5 rounded-full text-xs ${
                        task.priority === 'high' ? 'bg-red-500/10 text-red-600' : 'bg-yellow-500/10 text-yellow-600'
                      }`}>
                        {task.priority}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-24 bg-white/5 border-y border-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Everything you need</h2>
              <p className="text-muted-foreground">Powerful features wrapped in a stunning interface.</p>
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
                  desc: "Neo Glass Aurora UI that makes work feel like play."
                }
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="glass-panel p-8 hover:bg-white/10 transition-colors"
                >
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-6">
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.desc}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-black/5">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-primary/20" />
            <span className="font-semibold">iTasks</span>
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
