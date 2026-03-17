import type { Metadata } from "next";
import Script from "next/script";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/lib/auth-provider";
import "./globals.css";

import { PageTransitionWrapper } from "@/components/page-transition-wrapper"; // New import

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "iTasks - Phase 2",
  description: "iTasks: Organize your life with elegance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Load ChatKit Web Component from Official OpenAI CDN */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />

        <Toaster />
        <AuthProvider>
          <PageTransitionWrapper>
            {children}
          </PageTransitionWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}
