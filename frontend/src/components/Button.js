export default function Button({ text, onClick, type = "button", disabled = false }) {
  return (
    <button 
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`w-full font-bold py-3 px-4 rounded-lg shadow-lg transition-all duration-300 
        ${disabled ? "bg-slate-500 cursor-not-allowed text-slate-300" : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/50"}`}
    >
      {text}
    </button>
  );
}