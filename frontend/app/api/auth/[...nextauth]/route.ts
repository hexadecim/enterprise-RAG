import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth.config";

/**
 * Route handler for all NextAuth endpoints:
 *   GET  /api/auth/signin
 *   GET  /api/auth/signout
 *   GET  /api/auth/session
 *   GET  /api/auth/providers
 *   GET  /api/auth/csrf
 *   GET  /api/auth/callback/:provider
 *   POST /api/auth/signin/:provider
 *   POST /api/auth/signout
 *   POST /api/auth/callback/:provider
 */
const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
