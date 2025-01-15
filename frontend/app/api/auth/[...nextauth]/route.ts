// app/api/auth/[...nextauth]/route.ts

import NextAuth from "next-auth";
import { authOptions } from "@/lib/authOptions";

const handler = NextAuth(authOptions);

// Exporting as GET and POST to handle both HTTP methods
export { handler as GET, handler as POST };
