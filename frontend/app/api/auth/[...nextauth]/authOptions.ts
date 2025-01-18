import CredentialsProvider from "next-auth/providers/credentials";
import { AuthOptions } from "next-auth";
import { authLogin } from "../../services/auth"; // Обновите путь, если необходимо
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      access?: string;
      refresh?: string;
    } & DefaultSession["user"];
  }

  interface User {
    access?: string;
    refresh?: string;
  }
}

export const authOptions: AuthOptions = {
  session: {
    strategy: "jwt",
  },
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email и пароль требуются");
        }

        // authLogin обращается к внешнему сервису (http://localhost:8000/api/auth/login/)
        const data = await authLogin(credentials.email, credentials.password);
        // Если успех, вернётся объект с токенами
        if (!data) {
          // Если нет, падаем с ошибкой
          throw new Error("Неверные учётные данные");
        }

        // Возвращаем объект с нужными данными
        return {
          id: data.id,
          access: data.access,
          refresh: data.refresh,
          email: credentials.email,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // При логине добавляем user данные в токен
      if (user) {
        token.access = user.access;
        token.refresh = user.refresh;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      // Прокидываем нужные данные из токена в session
      if (token?.access) {
        session.user = {
          ...session.user,
          id: token.id as string,
          access: token.access as string,
          refresh: token.refresh as string,
        };
      }
      return session;
    },
  },
  pages: {
    signIn: "/login", // Страница логина
  },
};
