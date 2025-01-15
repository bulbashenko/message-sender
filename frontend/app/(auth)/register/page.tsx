// app/auth/register/page.tsx
"use client";

import { FormEvent, useEffect, useState } from "react";
import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("NEXT_PUBLIC_BACKEND_URL is not defined in .env.local");
}

export default function RegisterPage() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { data: session, status } = useSession();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [status, router]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, username }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || JSON.stringify(errData) || "Register Error");
      }

      const loginRes = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (loginRes?.error) {
        throw new Error(loginRes.error);
      }

      router.push("/dashboard");
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Something went wrong";
      setError(errorMessage);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4">
        <h1 className="text-xl font-bold">Register</h1>
        {error && <p className="text-red-500">{error}</p>}

        <div>
          <label>Email</label>
          <Input
            type="email"
            onChange={(e) => setEmail(e.target.value)}
            value={email}
            required
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label>Password</label>
          <Input
            type="password"
            onChange={(e) => setPassword(e.target.value)}
            value={password}
            required
            placeholder="••••••"
          />
        </div>

        <Button type="submit" variant="default">
          Register
        </Button>

        <p className="text-sm mt-4">
          Do you have an account?{" "}
          <a href="/login" className="underline">
            Log In
          </a>
        </p>
      </form>
    </div>
  );
}
