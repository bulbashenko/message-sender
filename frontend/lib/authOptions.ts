// lib/authOptions.ts

/* eslint-disable @typescript-eslint/no-explicit-any */
import type { AuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import FacebookProvider from "next-auth/providers/facebook";

declare module "next-auth" {
  interface User {
    access: string;
    refresh: string;
  }
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("NEXT_PUBLIC_BACKEND_URL is not defined in .env.local");
}

export const authOptions: AuthOptions = {
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async signIn({ account }) {
      if (account?.provider === "facebook") {
        try {
          const response = await fetch(`${BACKEND_URL}/api/auth/login/facebook/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              access_token: account.access_token,
            }),
          });

          const data = await response.json();

          if (!response.ok) {
            console.error("[Facebook Login] Error:", data.error);
            return false;
          }

          // Store the JWT tokens
          account.access = data.data.access;
          account.refresh = data.data.refresh;
          return true;
        } catch (error) {
          console.error("[Facebook Login] Error:", error);
          return false;
        }
      }
      return true;
    },

    async jwt({ token, user, account }) {
      console.log("[JWT Callback] Начало обработки токена:", { token, user, account });

      if (account?.provider === "facebook") {
        token.access = account.access;
        token.refresh = account.refresh;
      } else if (user) {
        token.access = user.access;
        token.refresh = user.refresh;
      }

      console.log("[JWT Callback] Завершение обработки токена:", token);
      return token;
    },
    async session({ session, token }) {
      console.log("[Session Callback] Начало обработки сессии:", { session, token });

      // Передаём токены в сессию
      if (token) {
        (session as any).access = token.access;
        (session as any).refresh = token.refresh;
      }

      console.log("[Session Callback] Завершение обработки сессии:", session);
      return session;
    },
  },
  providers: [
    FacebookProvider({
      clientId: "965280662128440",
      clientSecret: "4e432e2f4f2b9a190995c4d39cd716ee"
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      // Логика авторизации
      async authorize(credentials) {
        console.log("[Authorize] Попытка авторизации пользователя с email:", credentials?.email);

        if (!credentials?.email || !credentials.password) {
          console.error("[Authorize] Отсутствует email или пароль");
          throw new Error("Missing email or password");
        }

        try {
          // Отправляем запрос на /api/auth/login/
          const res = await fetch(`${BACKEND_URL}/api/auth/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          const data = await res.json();
          console.log("[Authorize] Ответ от бэкенда:", data);

          if (!res.ok) {
            console.error("[Authorize] Ошибка при авторизации:", data.detail || "Login Error");
            throw new Error(data.detail || "Login Error");
          }

          const { access, refresh } = data.data;

          if (!access || !refresh) {
            console.error("[Authorize] Отсутствуют access или refresh токены:", data);
            throw new Error("Invalid response from server");
          }

          console.log("[Authorize] Успешная авторизация пользователя:", credentials.email);

          // Возвращаем токены и обязательное поле id
          return {
            id: credentials.email, // Using email as id
            access,
            refresh,
          };
        } catch (error) {
          console.error("[Authorize] Не удалось авторизоваться:", error);
          throw error;
        }
      },
    }),
  ],
};
