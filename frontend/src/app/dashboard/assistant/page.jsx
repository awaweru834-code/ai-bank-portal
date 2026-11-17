"use client";

import { useState, useEffect, useRef } from "react";
import { getChatHistory, sendChatMessage } from "@/services/api";

export default function AssistantPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef(null);

  // 1. Fetch History on Mount (Axios REST)
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await getChatHistory();
        if (history && history.length > 0) {
          // Normalize backend "assistant" roles to frontend "ai" roles for styling
          const formattedHistory = history.map(msg => ({
            ...msg,
            role: msg.role === "assistant" ? "ai" : msg.role
          }));
          setMessages(formattedHistory);
        } else {
          setMessages([{ role: "ai", content: "Hello. I am Hank, your autonomous institutional assistant. How can I manage your vault today?" }]);
        }
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    };
    
    loadHistory();
  }, []);

  // 2. Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 3. Handle Message Submission (Axios REST)
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userText = input;
    
    // Add user message to UI instantly and clear input
    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setInput("");
    setIsTyping(true);

    try {
      // Send the POST request to FastAPI
      const response = await sendChatMessage(userText);
      
      // Append the AI's response to the chat
      setMessages((prev) => [...prev, { role: "ai", content: response.content }]);
    } catch (error) {
      // Catch rate limits or network failures gracefully
      const errorMsg = error.message || "Network error. Please try again.";
      setMessages((prev) => [...prev, { role: "ai", content: ` ${errorMsg}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
      
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <span className="text-xl"></span> Hank Bank AI
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">Equipped with RAG Policy Retrieval & Live Vault Access</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Static green dot since standard REST is always "online" */}
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            System Online
          </span>
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div 
              className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                msg.role === "user" 
                  ? "bg-slate-900 text-white rounded-br-sm" 
                  : "bg-white border border-slate-200 text-slate-800 rounded-bl-sm"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-bl-sm shadow-sm flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce delay-75"></div>
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce delay-150"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-slate-100">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            placeholder="Ask Hank to check your balance or query a policy..."
            className="w-full pl-4 pr-12 py-3.5 bg-slate-100 border-none rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all disabled:opacity-50 text-slate-900 placeholder-slate-400"
          />
          <button
            type="submit"
            disabled={isTyping || !input.trim()}
            className="absolute right-2 p-2 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 disabled:opacity-50 disabled:hover:bg-emerald-500 transition-colors shadow-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}