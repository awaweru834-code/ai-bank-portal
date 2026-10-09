"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser, registerUser } from "@/services/api";
import UnsplashBackground from "@/components/UnsplashBackground";

export default function AuthPortal() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoginMode, setIsLoginMode] = useState(true); // The Toggle State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // 1. HANDLE FORM SUBMISSION
  const handleAuth = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      if (isLoginMode) {
        // LOGIN FLOW: HttpOnly cookie is set invisibly by the backend
        await loginUser(username, password);
        // Instantly transport them to the secure dashboard
        router.push("/dashboard"); 
      } else {
        // REGISTRATION FLOW
        await registerUser(username, password);
        alert("Account securely created! You can now log in.");
        setIsLoginMode(true); // Flip the UI back to Login mode automatically
        setPassword(""); // Clear the password field for security
      }
    } catch (error) {
      setError(error.message || "An error occurred. Please try again."); 
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center p-4 overflow-hidden">
      {/* 2. DYNAMIC BACKGROUND: Replaces the static local image */}
      <UnsplashBackground imageId="1616803140344-6682afb13cda" opacity="bg-slate-950/85" />

      {/* 3. GLASSMORPHIC AUTH CARD */}
      <div className="relative z-10 w-full max-w-md bg-slate-900/40 backdrop-blur-md border border-slate-700 p-8 rounded-2xl text-slate-200 shadow-2xl">
        <div className="flex justify-center mb-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-500 font-bold text-slate-950 flex items-center justify-center text-xl shadow-lg shadow-emerald-500/20">
            H
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-center mb-2">Hank Bank Portal</h1>
        <p className="text-center text-slate-400 mb-8">
          {isLoginMode ? "Authenticate to access the vault" : "Register for a secure account"}
        </p>

        {error && (
          <div className="mb-5 p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleAuth} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2 text-slate-300">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all placeholder-slate-500"
              placeholder="e.g. robert_del_naja"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2 text-slate-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all placeholder-slate-500"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-400 transition-colors text-slate-950 rounded-lg font-bold shadow-lg shadow-emerald-500/20 disabled:opacity-50"
          >
            {isLoading ? "Processing..." : isLoginMode ? "Secure Login" : "Create Account"}
          </button>
        </form>

        {/* 4. THE TOGGLE BUTTON */}
        <div className="mt-6 text-center">
          <button 
            type="button"
            onClick={() => {
              setIsLoginMode(!isLoginMode);
              setError(""); // Clear errors when flipping modes
            }}
            className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors font-medium"
          >
            {isLoginMode ? "Need an account? Sign Up" : "Already have an account? Log In"}
          </button>
        </div>
      </div>
    </main>
  );
}