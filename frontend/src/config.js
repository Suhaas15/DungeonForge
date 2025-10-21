// API Configuration
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
// Remove trailing slashes and dots
export const API_URL = apiUrl.replace(/[/.]+$/, '');

