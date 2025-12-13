import { Navbar } from "@/components/navbar";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen relative bg-background">
      <Navbar />
      
      <div className="fixed top-20 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none -z-10 animate-float" />
      <div className="fixed bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none -z-10 animate-float" style={{ animationDelay: "2s" }} />

      <main className="max-w-2xl mx-auto px-6 py-8 relative z-10">
        {children}
      </main>
    </div>
  );
}
