"use client";
import { useState } from "react";
import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import UnsplashBackground from "@/components/UnsplashBackground";

export default function DashboardLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden font-sans relative">
      <UnsplashBackground imageId="1557683316-973673baf926" opacity="bg-slate-950/95" />
      
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} pathname={pathname} />

      <main className="flex-1 overflow-y-auto p-8 relative z-10">
        {children}
      </main>
    </div>
  );
}