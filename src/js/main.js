import { ChatUI } from './chatUI.js';
import { ChatAPI } from './chatAPI.js';
import { ThemeManager } from './themeManager.js';

// Initialize chat components
const chatUI = new ChatUI();
const chatAPI = new ChatAPI(chatUI);
const themeManager = new ThemeManager();

// Add initial greeting
chatUI.addBotMessage("Hello! How can I help you today?");