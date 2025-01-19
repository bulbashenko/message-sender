import CredentialsProvider from "next-auth/providers/credentials";
import { AuthOptions } from "next-auth";
import { authLogin, authLoginFacebook, authLogout } from "../../services/auth";
import { DefaultSession } from "next-auth";
import FacebookProvider from "next-auth/providers/facebook"; // Импорт FacebookProvider


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

  interface JWT {
    access?: string;
    refresh?: string;
    id?: string;
  }
}

export const authOptions: AuthOptions = {
  session: {
    strategy: "jwt",
  },
  events: {
    async signOut({ token }) {
      if (token?.refresh && token?.access) {
        try {
          await authLogout(token.refresh as string, token.access as string);
        } catch (error) {
          console.error("Error during logout:", error);
        }
      }
    },
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

        const data = await authLogin(credentials.email, credentials.password);
        if (!data) {
          throw new Error("Неверные учётные данные");
        }

        return {
          id: data.id,
          access: data.access,
          refresh: data.refresh,
          email: credentials.email,
        };
      },
    }),
    // Добавляем FacebookProvider
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID as string,
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET as string,
      authorization: {
        params: {
          scope: "email,public_profile", // Запрашиваемые разрешения
          // Можно добавить другие параметры, если необходимо
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.access = user.access;
        token.refresh = user.refresh;
        token.id = user.id;
      }

      // Если пользователь авторизовался через Facebook
      if (account && account.provider === "facebook") {
        try {
          // Получаем access_token от Facebook
          const facebookAccessToken = account.access_token as string;
          const redirect_uri = process.env.FACEBOOK_REDIRECT_URI as string;

          // Отправляем access_token на ваш бэкенд для обмена на токены вашего приложения
          const authData = await authLoginFacebook(facebookAccessToken, redirect_uri);

          if (authData) {
            token.access = authData.access;
            token.refresh = authData.refresh;
            token.id = authData.id;
            // Можно добавить email, если необходимо
            token.email = authData.email;
          }
        } catch (error) {
          console.error("Error during Facebook login:", error);
        }
      }
      return token;
    },
    async session({ session, token }) {
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
    signIn: "/login",
  },
};
