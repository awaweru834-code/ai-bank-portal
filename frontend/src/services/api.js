import axios from "axios";


const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// 1. Create the Centralized Axios Engine
export const api = axios.create({
    baseURL: BASE_URL,
    // THIS IS THE MAGIC LINE: It forces Axios to attach the HttpOnly cookie to every request automatically.
    withCredentials: true, 
});

// 🛡️ THE SECURITY CHECKPOINT (Global Request Interceptor)
// DELETED! The browser now securely attaches the cookie itself. 
// No more manual Authorization headers or localStorage lookups!

// 🛡️ THE COLD START & BOUNCER (Global Response Interceptor)
api.interceptors.response.use(
    (response) => response, 
    (error) => {
        // 1. Cold Start Catcher (For Render's sleep cycle)
        if (error.message === "Network Error" || error.code === "ERR_NETWORK") {
            return Promise.reject(new Error("The secure vault is waking up! Please wait 30 seconds and try again."));
        }
        
        // 2. The 401 Interceptor (Session Expired)
        if (error.response?.status === 401) {
            // We no longer need to clear localStorage because the token isn't there.
            window.location.href = "/login"; // Automatically boot them to the login page
            return Promise.reject(new Error("SESSION_EXPIRED"));
        }
        
        return Promise.reject(error); 
    }
);

// 1. The Sign Up Doorway
export const registerUser = async (username, password) => {
    try {
        const { data } = await api.post("/users/", { username, password, balance: 1000 });
        return data; 
    } catch (error) {
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw error; 
    }
};

// 2. The Login Doorway
export const loginUser = async (username, password) => {
    try {
        const formData = new URLSearchParams({ username, password });

        const { data } = await api.post("/token", formData, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
        
        // DELETED localStorage.setItem()! 
        // FastAPI's response.set_cookie() handles storing the token safely in the browser.
        
        return data;
    } catch (error) {
        if (error.response) {
            throw new Error("Invalid username or password");
        }
        throw error;
    }
};

// 3. The Chat Doorway
export const sendChatMessage = async (message, mode = "bank") => {
    try {
        const endpoint = mode === "policy_checker" ? "/ask-pdf" : "/bank-chat";
        const payload = mode === "policy_checker" 
            ? { user_question: message } 
            : { user_text: message };

        const { data } = await api.post(endpoint, payload);
        
        return data;
    } catch (error) {
        throw error;
    }
};

// ==========================================
// WEBSOCKET CONFIGURATION
// ==========================================
export const getWebSocketUrl = () => {
    // If testing on localhost, use 'ws://'. 
    // If deployed on Render, MUST use 'wss://' (secure).
    
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    
    // DELETED the ?token= URL parameter!
    // The browser automatically sends the HttpOnly cookie during the WebSocket handshake.
    return `${WS_URL}/ws/chat`;
};