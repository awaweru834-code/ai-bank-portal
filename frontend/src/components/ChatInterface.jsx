import { useState } from "react";
import { sendChatMessage } from "../services/api";
import Button from "./Button";

export default function ChatInterface({ token, onLogout }) {
  const [messages, setMessages] = useState([
    { role: "ai", text: "Welcome to the AI Portal. Select your assistant mode above." }
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Track which brain we are talking to
  const [chatMode, setChatMode] = useState("bank");

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const newMessages = [...messages, { role: "user", text: inputText }];
    setMessages(newMessages);
    setInputText("");
    setIsLoading(true);

    try {
      // Pass the chatMode to the API
      const response = await sendChatMessage(inputText, token, chatMode);
      
      // Update with AI's reply
      setMessages([...newMessages, { role: "ai", text: response.ai_reply || response }]);
    } catch (error) {
      // 🛑 THE 401 EXPIRY & COLD START INTERCEPTOR
      if (error.message === "SESSION_EXPIRED") {
        alert("Your secure session has expired. Please log in again.");
        onLogout(); // Instantly kicks them out and wipes localStorage
      } else {
        // Handles standard errors AND the "Waking Up" cold start message
        alert(error.message);
        setMessages([...newMessages, { role: "ai", text: `❌ ${error.message}` }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden mt-8">
      
      {/* Header with Logout */}
      <div className="flex justify-between items-center p-4 bg-slate-900/80 border-b border-slate-700/50">
        <h2 className="text-xl font-bold text-white">Financial Assistant</h2>
        <button onClick={onLogout} className="text-sm text-slate-400 hover:text-white transition-colors">
          Secure Logout
        </button>
      </div>

      {/* The Mode Toggle Switch */}
      <div className="flex justify-center p-3 bg-slate-800/80 border-b border-slate-700/50 gap-2">
        <button 
          onClick={() => setChatMode("bank")}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
            chatMode === "bank" ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30" : "bg-slate-700 text-slate-400 hover:bg-slate-600"
          }`}
        >
          🏦 Bank Assistant
        </button>
        <button 
          onClick={() => setChatMode("policy_checker")}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
            chatMode ===  "policy_checker"? "bg-purple-600 text-white shadow-lg shadow-purple-500/30" : "bg-slate-700 text-slate-400 hover:bg-slate-600"
          }`}
        >
          📄 Policy Checker
        </button>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl ${
              msg.role === "user" 
                ? "bg-blue-600 text-white rounded-br-sm shadow-blue-500/20" 
                : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-sm"
            } shadow-lg`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-400 border border-slate-700 p-4 rounded-2xl rounded-bl-sm animate-pulse">
              AI is thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-4 bg-slate-900/80 border-t border-slate-700/50">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={chatMode === "bank" ? "Ask about your balance..." : "Ask about company policies..."}
            className="flex-1 bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
            disabled={isLoading}
          />
          <div className="w-24">
            <Button type="submit" text="Send" disabled={isLoading || !inputText.trim()} />
          </div>
        </form>
      </div>
    </div>
  );
}