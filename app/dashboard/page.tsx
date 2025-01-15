"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("NEXT_PUBLIC_BACKEND_URL is not defined in .env.local");
}

declare module "next-auth" {
  interface Session {
    user?: {
      email?: string | null;
    };
    access?: string;
    refresh?: string;
  }
}

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Состояния для WhatsApp
  const [whatsAppNumber, setWhatsAppNumber] = useState("");
  const [whatsAppMessage, setWhatsAppMessage] = useState("");
  // Состояния для Email
  const [emailTo, setEmailTo] = useState("");
  const [emailSubject, setEmailSubject] = useState("");
  const [emailMessage, setEmailMessage] = useState("");

  // Общий вывод статуса / ошибок
  const [feedback, setFeedback] = useState("");

  // Если пользователь не авторизован — отправляем на /auth/login
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Логаут: сначала инвалидируем токен на бекенде, затем вызываем signOut
  async function handleLogout() {
    try {
      const accessToken = session?.access;
      const refreshToken = session?.refresh;

      // Если нет токенов, вероятно, уже не авторизованы — просто signOut
      if (!accessToken || !refreshToken) {
        return signOut({ callbackUrl: "/login" });
      }

      // 1. Вызываем /api/auth/logout/ на бекенде
      const logoutRes = await fetch(`${BACKEND_URL}/api/auth/logout/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!logoutRes.ok) {
        // Можно вывести предупреждение, но всё равно делать signOut
        const errorData = await logoutRes.json();
        console.error("Logout on backend failed:", errorData);
      }

      // 2. После этого очищаем клиентскую сессию (NextAuth)
      signOut({ callbackUrl: "/login" });
    } catch (error) {
      console.error("Logout error:", error);
      signOut({ callbackUrl: "/login" });
    }
  }

  // Вспомогательная функция для отправки запросов на WhatsApp/Email
  async function callApi(url: string, bodyData: object) {
    const accessToken = session?.access;
    setFeedback(""); // очистим предыдущий статус

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`, // используем access-токен из сессии
      },
      body: JSON.stringify(bodyData),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Error sending message");
    }

    return data;
  }

  // Отправка WhatsApp
  async function sendWhatsApp() {
    try {
      const result = await callApi(
        `${BACKEND_URL}/api/communications/whatsapp/send/`,
        {
          to: whatsAppNumber,
          message: whatsAppMessage,
        },
      );
      setFeedback(`WhatsApp Success: ${JSON.stringify(result)}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setFeedback(`WhatsApp Error: ${err.message}`);
      } else {
        setFeedback(`WhatsApp Error: Unknown error`);
      }
    }
  }

  // Отправка Email
  async function sendEmail() {
    try {
      const result = await callApi(
        `${BACKEND_URL}/api/communications/email/send/`,
        {
          to: emailTo,
          subject: emailSubject,
          message: emailMessage,
        },
      );
      setFeedback(`Email Success: ${JSON.stringify(result)}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setFeedback(`Email Error: ${err.message}`);
      } else {
        setFeedback(`Email Error: Unknown error`);
      }
    }
  }

  // Пока идёт загрузка сессии
  if (status === "loading") {
    return <p>Loading...</p>;
  }
  // Если нет сессии, рендерим пустую страницу (редирект сработает выше)
  if (!session) {
    return null;
  }

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-xl font-bold">Welcome to Dashboard!</h1>
      <p>You are logged in as: {session.user?.email}</p>
      <Button onClick={handleLogout} variant="destructive">
        Logout
      </Button>

      <hr className="my-4" />

      {/* Блок WhatsApp */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Send WhatsApp Message</h2>
        <div className="mb-2">
          <label>Phone Number</label>
          <Input
            type="text"
            value={whatsAppNumber}
            onChange={(e) => setWhatsAppNumber(e.target.value)}
            placeholder="+1234567890"
          />
        </div>
        <div className="mb-2">
          <label>Message</label>
          <Textarea
            value={whatsAppMessage}
            onChange={(e) => setWhatsAppMessage(e.target.value)}
            placeholder="Your text..."
          />
        </div>
        <Button onClick={sendWhatsApp}>Send WhatsApp</Button>
      </section>

      <hr className="my-4" />

      {/* Блок Email */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Send Email</h2>
        <div className="mb-2">
          <label>Recipient (To)</label>
          <Input
            type="email"
            value={emailTo}
            onChange={(e) => setEmailTo(e.target.value)}
            placeholder="recipient@example.com"
          />
        </div>
        <div className="mb-2">
          <label>Subject</label>
          <Input
            type="text"
            value={emailSubject}
            onChange={(e) => setEmailSubject(e.target.value)}
            placeholder="Welcome to Our Platform"
          />
        </div>
        <div className="mb-2">
          <label>Message</label>
          <Textarea
            value={emailMessage}
            onChange={(e) => setEmailMessage(e.target.value)}
            placeholder="Your text..."
          />
        </div>
        <Button onClick={sendEmail}>Send Email</Button>
      </section>

      {/* Отображение результата (feedback) */}
      {feedback && (
        <p className="mt-4 whitespace-pre-wrap text-sm text-green-600">
          {feedback}
        </p>
      )}
    </div>
  );
}
