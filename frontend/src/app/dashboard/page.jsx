"use client";

import { useState, useEffect } from "react";
import { api } from "@/services/api";

export default function DashboardHome() {
  const [profile, setProfile] = useState(null);
  const [blurBalance, setBlurBalance] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetches live user profile using HttpOnly cookie authentication
    api.get("/users/me")
      .then((res) => {
        setProfile(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching account profile:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-slate-800">
      
      {/* Top Banner & Balance Component */}
      <section className="bg-white/80 backdrop-blur-md rounded-3xl p-8 border border-slate-200/80 shadow-lg grid md:grid-cols-3 gap-8 items-center">
        
        {/* Balance Panel */}
        <div className="md:col-span-1 border-r border-slate-200/60 pr-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Live Vault Balance
            </span>
            <button
              onClick={() => setBlurBalance(!blurBalance)}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
            >
              {blurBalance ? "Reveal" : "Hide"}
            </button>
          </div>
          
          <div
            className={`text-4xl font-extrabold text-slate-900 tracking-tight transition-all duration-300 cursor-pointer ${
              blurBalance ? "filter blur-md select-none" : ""
            }`}
            onClick={() => setBlurBalance(!blurBalance)}
          >
            {loading 
              ? "Loading..." 
              : profile 
                ? `$${profile.balance.toLocaleString("en-US", { minimumFractionDigits: 2 })}` 
                : "$0.00"}
          </div>
          
          <p className="text-xs text-slate-400 mt-2">
            Account Holder: <span className="font-semibold text-slate-700">{profile?.username || "Authenticated User"}</span>
          </p>
        </div>

        {/* Loan Cards (Inspired by reference UI) */}
        <div className="md:col-span-2 grid sm:grid-cols-3 gap-4">
          <div className="bg-slate-50/80 border border-slate-200/60 p-4 rounded-2xl shadow-sm">
            <span className="text-xl">🏡</span>
            <p className="text-xs text-slate-500 mt-2">Family house loan</p>
            <p className="text-base font-bold text-slate-900">-$120,000</p>
            <p className="text-[10px] text-slate-400">Balance owing</p>
          </div>
          <div className="bg-slate-50/80 border border-slate-200/60 p-4 rounded-2xl shadow-sm">
            <span className="text-xl">🏛️</span>
            <p className="text-xs text-slate-500 mt-2">Eurotrip loan</p>
            <p className="text-base font-bold text-slate-900">-$21,489</p>
            <p className="text-[10px] text-slate-400">Balance owing</p>
          </div>
          <div className="bg-slate-50/80 border border-slate-200/60 p-4 rounded-2xl shadow-sm">
            <span className="text-xl">🚗</span>
            <p className="text-xs text-slate-500 mt-2">Vehicle loan</p>
            <p className="text-base font-bold text-slate-900">-$2,312</p>
            <p className="text-[10px] text-slate-400">Balance owing</p>
          </div>
        </div>
      </section>

      {/* Institutional Documents & Verification Table */}
      <section className="bg-white/80 backdrop-blur-md rounded-3xl p-8 border border-slate-200/80 shadow-lg space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Institutional Docs</h3>
        <div className="divide-y divide-slate-100 text-sm">
          {[
            { name: "Government National ID", status: "Verified", time: "19 Mar, 2:51 PM", color: "text-emerald-700 bg-emerald-50 border border-emerald-200/50" },
            { name: "Bank Verification Statement", status: "Waiting", time: "07 Mar, 6:44 PM", color: "text-amber-700 bg-amber-50 border border-amber-200/50" },
            { name: "Commercial Registration", status: "Verified", time: "07 Mar, 10:01 AM", color: "text-emerald-700 bg-emerald-50 border border-emerald-200/50" },
          ].map((doc, idx) => (
            <div key={idx} className="py-3.5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-slate-400">📄</span>
                <span className="font-medium text-slate-800">{doc.name}</span>
              </div>
              <div className="flex items-center gap-6">
                <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${doc.color}`}>
                  {doc.status}
                </span>
                <span className="text-xs text-slate-400">{doc.time}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
      
    </div>
  );
}