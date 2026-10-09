"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser } from "@/services/api";
import UnsplashBackground from "@/components/UnsplashBackground";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await loginUser(username, password);
      router.push("/dashboard");
    } catch (err) {
      alert(err.message || "Login failed");
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4">
      <UnsplashBackground imageId="1616803140344-6682afb13cda" opacity="bg-slate-950/90" />
      
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-xl p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-white tracking-tight">Sign in to Hank</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-slate-950/50 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
            placeholder="Username"
          />
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-slate-950/50 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
            placeholder="Password"
          />
          <button type="submit" className="w-full py-3 rounded-lg bg-emerald-500 text-slate-950 font-bold text-sm hover:bg-emerald-400 transition-all mt-2">
            Open Vault
          </button>
        </form>
      </div>
    </div>
  );
}