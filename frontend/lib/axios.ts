// lib/axios.ts
import axios from "axios";

// Базовый адрес вашего бэкенда
const BASE_URL = "http://192.168.0.102:8000";

// Создаём экземпляр axios с дефолтными настройками
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Пример перехватчика (interceptor) для добавления токена:
api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("access_token"); 
  // Или, если у вас NextAuth, возможно брать токен из cookies/session
  // config.headers["Authorization"] = `Bearer ${accessToken}`;
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
