import type { NextAuthOptions, Session } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

// ---------------------------------------------------------------------------
// Helper: extract tenant_id from an email address
// e.g.  "alice@acme.com"  →  "acme.com"
//       "bob@corp.org"    →  "corp.org"
// ---------------------------------------------------------------------------
function extractTenantId(email: string | null | undefined): string {
    if (!email) return "unknown";
    const parts = email.split("@");
    return parts.length === 2 ? parts[1].toLowerCase() : "unknown";
}

// ---------------------------------------------------------------------------
// NextAuth configuration
// ---------------------------------------------------------------------------
export const authOptions: NextAuthOptions = {
    // ── Providers ────────────────────────────────────────────────────────────
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
            authorization: {
                params: {
                    // Request offline access so we get a refresh_token
                    access_type: "offline",
                    prompt: "consent",
                    scope: "openid email profile",
                },
            },
        }),
    ],

    // ── Session strategy ─────────────────────────────────────────────────────
    session: {
        strategy: "jwt",
        // 8-hour sliding window; adjust for your security policy
        maxAge: 8 * 60 * 60,
    },

    // ── JWT ──────────────────────────────────────────────────────────────────
    jwt: {
        // NEXTAUTH_SECRET is used as the signing/encryption key automatically
        maxAge: 8 * 60 * 60,
    },

    // ── Callbacks ────────────────────────────────────────────────────────────
    callbacks: {
        /**
         * jwt – called whenever a JWT is created or updated.
         * On first sign-in `user` and `account` are populated; on subsequent
         * requests only `token` is available.
         */
        async jwt({ token, user, account }) {
            if (account && user) {
                // First sign-in: enrich the JWT with custom claims
                token.email = user.email ?? token.email;
                token.name = user.name ?? token.name;
                token.picture = user.image ?? (token.picture as string | undefined);
                token.tenant_id = extractTenantId(user.email);
                token.accessToken = account.access_token;
                token.provider = account.provider;
            }
            return token;
        },

        /**
         * session – shapes the client-visible session object.
         * Never expose raw access tokens here — only what the UI actually needs.
         */
        async session({ session, token }) {
            if (session.user) {
                session.user.email = token.email as string;
                session.user.name = token.name as string;
                session.user.image = token.picture as string | undefined;
            }
            // Attach custom claims — typed via types/next-auth.d.ts augmentation
            (session as Session).tenant_id = token.tenant_id;
            (session as Session).provider = token.provider;
            return session;
        },
    },

    // ── Cookie configuration ─────────────────────────────────────────────────
    cookies: {
        sessionToken: {
            name:
                process.env.NODE_ENV === "production"
                    ? "__Secure-next-auth.session-token"  // HTTPS-only prefix
                    : "next-auth.session-token",
            options: {
                httpOnly: true,
                sameSite: "lax",
                path: "/",
                // secure: true is enforced in production; false in dev so localhost works
                secure: process.env.NODE_ENV === "production",
            },
        },
        callbackUrl: {
            name:
                process.env.NODE_ENV === "production"
                    ? "__Secure-next-auth.callback-url"
                    : "next-auth.callback-url",
            options: {
                httpOnly: true,
                sameSite: "lax",
                path: "/",
                secure: process.env.NODE_ENV === "production",
            },
        },
        csrfToken: {
            name:
                process.env.NODE_ENV === "production"
                    ? "__Host-next-auth.csrf-token"   // __Host- prefix = max restrictions
                    : "next-auth.csrf-token",
            options: {
                httpOnly: true,
                sameSite: "lax",
                path: "/",
                secure: process.env.NODE_ENV === "production",
            },
        },
    },

    // ── Pages (optional overrides) ───────────────────────────────────────────
    pages: {
        signIn: "/auth/signin",   // custom sign-in page (create later)
        error: "/auth/error",     // custom error page (create later)
    },

    // ── Security ─────────────────────────────────────────────────────────────
    secret: process.env.NEXTAUTH_SECRET,

    // Debug logging in development only
    debug: process.env.NODE_ENV === "development",
};
