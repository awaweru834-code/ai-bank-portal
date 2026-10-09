import { useState, useEffect, useRef } from "react";
import { getWebSocketUrl } from "../services/api";
import Button from "./Button";

export default function ChatInterface({ onLogout }) {
  const [messages, setMessages] = useState([
    { role: "ai", text: "Welcome to the AI Assistant. How can I help you today?" }
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const ws = useRef(null);

  useEffect(() => {
    const wsUrl = getWebSocketUrl();
    
    // Create a local variable so React Strict Mode doesn't confuse multiple connections
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onmessage = (event) => {
      const incomingText = event.data;
      setIsLoading(false);

      if (incomingText === "SESSION_EXPIRED") {
        alert("Your secure session has expired. Please log in again.");
        onLogout();
        return;
      }

      if (incomingText === "[DONE]") return; 

      setMessages((prevMessages) => {
        const lastMsg = prevMessages[prevMessages.length - 1];

        if (lastMsg.role === "user") {
          return [...prevMessages, { role: "ai", text: incomingText }];
        }

        const updatedMessages = [...prevMessages];
        updatedMessages[updatedMessages.length - 1] = {
          ...lastMsg,
          text: lastMsg.text + incomingText,
        };
        return updatedMessages;
      });
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
      setIsLoading(false);
      setMessages((prev) => [...prev, { role: "ai", text: "❌ Connection to server lost." }]);
    };

    // Clean up the exact socket instance created in this effect
    return () => {
      socket.close();
    };
  }, [onLogout]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: inputText }]);
    setInputText("");
    setIsLoading(true);

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(inputText);
    } else {
      alert("Still connecting to server, please try again in a moment.");
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden mt-8">
      
      <div className="flex justify-between items-center p-4 bg-slate-900/80 border-b border-slate-700/50">
        <h2 className="text-xl font-bold text-white">AI Assistant (Live Connection)</h2>
        <button onClick={onLogout} className="text-sm text-slate-400 hover:text-white transition-colors">
          Secure Logout
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl ${
              msg.role === "user" 
                ? "bg-blue-600 text-white rounded-br-sm shadow-blue-500/20" 
                : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-sm"
            } shadow-lg whitespace-pre-wrap`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-400 border border-slate-700 p-4 rounded-2xl rounded-bl-sm animate-pulse">
              AI is typing...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-900/80 border-t border-slate-700/50">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask me anything..."
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