/**
 * NextAuth module augmentation
 *
 * Extend the built-in types so TypeScript knows about our custom fields
 * (`tenant_id`, `provider`, `accessToken`) on Session and JWT.
 */
import type { DefaultSession, DefaultJWT } from "next-auth";

declare module "next-auth" {
    interface Session extends DefaultSession {
        /** Email domain used as a tenant identifier, e.g. "acme.com" */
        tenant_id: string;
        /** OAuth provider used to sign in, e.g. "google" */
        provider: string;
        user: {
            email: string;
            name: string;
            image?: string;
        } & DefaultSession["user"];
    }
}

declare module "next-auth/jwt" {
    interface JWT extends DefaultJWT {
        tenant_id: string;
        provider: string;
        accessToken?: string;
    }
}
