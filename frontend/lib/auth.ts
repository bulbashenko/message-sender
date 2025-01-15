// lib/auth.ts

import { getServerSession } from "next-auth";
import { authOptions } from "./authOptions";

/**
 * Retrieves the current user's session on the server side.
 *
 * @returns The user's session or null if not authenticated.
 */
export const getAuthSession = async () => {
  return await getServerSession(authOptions);
};
