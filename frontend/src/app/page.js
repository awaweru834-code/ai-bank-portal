"use client";
import { useState, useEffect } from "react";
import { loginUser, registerUser } from "../services/api";
import ChatInterface from "../components/ChatInterface";

export default function BankPortal() {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoginMode, setIsLoginMode] = useState(true); // The Toggle State
  const [isLoading, setIsLoading] = useState(false);

  // 1. CHECK MEMORY ON LOAD
  useEffect(() => {
    const savedToken = localStorage.getItem("bank_token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  // 2. HANDLE FORM SUBMISSION
  const handleAuth = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      if (isLoginMode) {
        // LOGIN FLOW
        const data = await loginUser(username, password);
        setToken(data.access_token);
        localStorage.setItem("bank_token", data.access_token); // Save to browser memory
      } else {
        // REGISTRATION FLOW
        await registerUser(username, password);
        alert("Account securely created! You can now log in.");
        setIsLoginMode(true); // Flip the UI back to Login mode automatically
      }
    } catch (error) {
      alert(error.message); // This will display the "Server Waking Up" message!
    } finally {
      setIsLoading(false);
    }
  };

  // 3. SECURE LOGOUT
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("bank_token"); // Wipe browser memory
    setUsername("");
    setPassword("");
  };

  // If token exists, show the chat!
  if (token) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950 bg-[url('/images/bank-bg.jpg')] bg-cover bg-center p-4">
        <ChatInterface token={token} onLogout={handleLogout} />
      </div>
    );
  }

  // Otherwise, show the Auth Portal
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 bg-[url('/images/bank-bg.jpg')] bg-cover bg-center p-4">
      <div className="w-full max-w-md bg-slate-900/10 backdrop-blur-sm border border-slate-700 p-8 rounded-2xl text-slate-200">
        <h1 className="text-3xl font-bold text-center mb-2">AI Bank Portal</h1>
        <p className="text-center text-slate-400 mb-8">
          {isLoginMode ? "Authenticate to access the vault" : "Register for a secure account"}
        </p>

        <form onSubmit={handleAuth} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 transition-colors rounded-lg font-semibold shadow-lg disabled:opacity-50"
          >
            {isLoading ? "Processing..." : isLoginMode ? "Secure Login" : "Create Account"}
          </button>
        </form>

        {/* THE TOGGLE BUTTON */}
        <div className="mt-6 text-center">
          <button 
            onClick={() => setIsLoginMode(!isLoginMode)}
            className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            {isLoginMode ? "Need an account? Sign Up" : "Already have an account? Log In"}
          </button>
        </div>
      </div>
    </main>
  );
}