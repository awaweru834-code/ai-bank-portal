"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    api.get("/users/me")
      .then((res) => setProfile(res.data))
      .catch((err) => console.error(err));
  }, []);

  const handleDeleteAccount = async () => {
    if (!confirm("Are you sure? This will permanently delete your account and balance data.")) return;
    try {
      await api.delete("/users/me");
      router.push("/login");
    } catch (err) {
      alert("Failed to delete account");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-sm text-slate-400">Manage user credentials and institutional data controls</p>
      </div>

      <div className="bg-slate-900/60 backdrop-blur-md rounded-2xl p-6 border border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-semibold">Account Profile</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-xs text-slate-500">Account ID</p>
            <p className="font-mono font-semibold">{profile?.id ?? "Loading..."}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Registered Username</p>
            <p className="font-semibold">{profile?.username ?? "Loading..."}</p>
          </div>
        </div>
      </div>

      <div className="bg-red-950/30 border border-red-900/50 rounded-2xl p-6 space-y-4">
        <div>
          <h3 className="text-base font-semibold text-red-400">Danger Zone</h3>
          <p className="text-xs text-red-300 mt-1">Permanently remove your account and all associated records.</p>
        </div>
        <button
          onClick={handleDeleteAccount}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors shadow-sm"
        >
          Delete Account
        </button>
      </div>
    </div>
  );
}