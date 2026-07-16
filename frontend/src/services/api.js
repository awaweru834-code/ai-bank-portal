const BASE_URL = "https://ai-bank-portal.onrender.com";

// 🛡️ THE COLD START CATCHER
// If the server is sleeping, fetch() throws a specific "Failed to fetch" TypeError.
const handleNetworkError = (error) => {
    if (error.message.includes("Failed to fetch")) {
        throw new Error("The secure vault is waking up! 🚀 Please wait 30 seconds and try again.");
    }
    throw error; // If it's a different error, pass it down
};

// 1. The Sign Up Doorway
export const registerUser = async (username, password) => {
    try {
        const response = await fetch(`${BASE_URL}/users/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Sending a default balance of $1000 so new users can test the tools
            body: JSON.stringify({ username: username, password: password, balance: 1000 }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Registration failed");
        }
        return response.json();
    } catch (error) {
        handleNetworkError(error);
    }
};

// 2. The Login Doorway
export const loginUser = async (username, password) => {
    try {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${BASE_URL}/token`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });

        if (!response.ok) throw new Error("Invalid username or password");
        return response.json();
    } catch (error) {
        handleNetworkError(error);
    }
};

// 3. The Chat Doorway
export const sendChatMessage = async (message, token, mode = "bank") => {
    try {
        const endpoint = mode === "policy_checker" ? "/ask-pdf" : "/bank-chat";
        const payload = mode === "policy_checker" 
            ? { user_question: message } 
            : { user_text: message };

        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload),
        });

        // 🛑 THE 401 INTERCEPTOR
        // If the JWT is expired, FastAPI returns 401. We intercept it here.
        if (response.status === 401) {
            throw new Error("SESSION_EXPIRED");
        }

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
    } catch (error) {
        handleNetworkError(error);
    }
};