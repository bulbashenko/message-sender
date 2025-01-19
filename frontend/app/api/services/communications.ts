// app/api/services/communications.ts
"use server"
import axios from "axios";

const BASE_URL = process.env.BASE_BACKEND_URL;
if (!BASE_URL) {
  throw new Error("BASE_BACKEND_URL is not defined in the environment variables");
}

export async function sendEmail(
  accessToken: string,
  to: string,
  subject: string,
  message: string,
) {
  const res = await axios.post(
    `${BASE_URL}/api/communications/email/`,
    { to, subject, message },
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );
  return res.data;
}

export async function sendWhatsApp(
  accessToken: string,
  to: string,
  message: string,
) {
  const res = await axios.post(
    `${BASE_URL}/api/communications/whatsapp/`,
    {
      to,
      message_type: "text",
      message,
    },
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );
  return res.data;
}
