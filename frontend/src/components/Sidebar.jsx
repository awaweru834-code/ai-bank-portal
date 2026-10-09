import Link from "next/link";

export default function Sidebar({ collapsed, setCollapsed, pathname }) {
  const navItems = [
    { label: "Overview", href: "/dashboard", icon: "🏦" },
    { label: "Hank AI Assistant", href: "/dashboard/assistant", icon: "🤖" },
    { label: "Settings", href: "/dashboard/settings", icon: "⚙️" },
  ];

  return (
    <aside
      className={`bg-slate-900 border-r border-slate-800 transition-all duration-300 flex flex-col justify-between p-4 relative z-20 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-8 px-2">
          {!collapsed && <span className="font-extrabold text-xl tracking-tight text-white">Hank Bank</span>}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors mx-auto"
          >
            {collapsed ? ">" : "<"}
          </button>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                  isActive ? "bg-emerald-500 text-slate-950 shadow-sm" : "text-slate-400 hover:bg-slate-800 hover:text-white"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <span className="text-base">{item.icon}</span>
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </div>
      {!collapsed ? (
        <div className="rounded-2xl p-4 bg-gradient-to-tr from-[#583D9E] to-[#7E57C2] text-white shadow-md">
          <div className="flex justify-between items-center text-xs opacity-80 mb-2">
           <span>Debit</span>
           <span className="font-semibold italic">VISA</span>
          </div>
          <p className="text-xs opacity-75">Card Balance</p>
    
          {/* THE FIX: Render the dynamic balance variable here */}
          <p className="text-lg font-bold tracking-tight mb-2">
            ${balance !== undefined 
            ? balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) 
            : "0.00"}
          </p>
    
          <p className="text-[11px] font-mono tracking-widest opacity-80">•••• 5008</p>
        </div>
     ) : (
        <div className="w-10 h-10 rounded-xl bg-[#583D9E] text-white flex items-center justify-center font-bold text-xs mx-auto">
          💳
        </div>
     )}
      
      
    </aside>
  );
}