import axios from "axios";


const BASE_URL = process.env.NEXT_PUBLIC_API_URL || " https://ai-bank-portal-6.onrender.com";

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

        const { data } = await api.post("/login", formData, {
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


export const sendChatMessage = async (message) => {
    try {
        const { data } = await api.post("/ai/chat", { message: message });
        return data;
    } catch (error) {
        // If the rate limiter blocks it, throw a user-friendly error
        if (error.response?.status === 429) {
            throw new Error("Too many messages. Please wait a moment.");
        }
        throw new Error("Failed to send message.");
    }
};


// 3. The Chat History Doorway
// Automatically fetches the last 10 messages from the database on page load
export const getChatHistory = async () => {
    try {
        const { data } = await api.get("/ai/history");
        return data;
    } catch (error) {
        console.error("Failed to load chat history:", error);
        return []; // Return an empty array on failure so the UI doesn't crash
    }
};

// 5. The Delete Account Doorway
// Triggers the DELETE /users/me endpoint to wipe the user's data and terminate the session cookie
export const deleteAccount = async () => {
    try {
        const { data } = await api.delete("/users/delete");
        return data;
    } catch (error) {
        // Safely extract the FastAPI error message if one is provided
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        // Fallback error message
        throw new Error("Failed to delete account. Please try again later.");
    }
};