import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "react-hot-toast";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Evolved Todo",
  description: "Next Gen Task Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* CRITICAL: ChatKit Web Component Library */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950 text-slate-200`}
      >
        {children}

        {/* EVOLVED OS TOAST CONFIGURATION */}
        <Toaster
          position="top-right" // <--- CHANGED TO TOP-RIGHT
          toastOptions={{
            className: "",
            duration: 4000,
            style: {
              background: "#020617", // slate-950
              color: "#e2e8f0",      // slate-200
              border: "1px solid #1e293b", // slate-800
              padding: "12px 16px",
              borderRadius: "2px",   // rounded-sm (Sharp corners)
              fontFamily: "var(--font-geist-mono)",
              fontSize: "12px",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              boxShadow: "0 0 20px rgba(6, 182, 212, 0.1)", // Subtle cyan glow
            },
            success: {
              iconTheme: {
                primary: "#06b6d4", // cyan-500
                secondary: "#020617",
              },
              style: {
                border: "1px solid rgba(6, 182, 212, 0.3)", // Cyan border
                color: "#22d3ee", // cyan-400 text
              }
            },
            error: {
              iconTheme: {
                primary: "#ef4444", // red-500
                secondary: "#020617",
              },
              style: {
                border: "1px solid rgba(239, 68, 68, 0.3)", // Red border
                color: "#f87171", // red-400 text
              }
            },
          }}
        />
      </body>
    </html>
  );
}