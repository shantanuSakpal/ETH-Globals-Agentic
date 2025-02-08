// frontend/app/(auth)/auth.ts
import { cookies } from "next/headers";
import crypto from "crypto";
import { getUser, createUser } from "@/lib/db/queries";

function getUUIDFromWallet(walletAddress: string): string {
  const NAMESPACE = "6ba7b810-9dad-11d1-80b4-00c04fd430c8";
  return crypto
    .createHash("sha1")
    .update(NAMESPACE + walletAddress)
    .digest()
    .subarray(0, 16)
    .toString("hex")
    .replace(/(.{8})(.{4})(.{4})(.{4})(.{12})/, "$1-$2-$3-$4-$5");
}

export interface User {
  id: string;
  email?: string;
  walletAddress?: string;
}

export async function auth(): Promise<{ user?: User | null }> {
  try {
    const cookieStore = cookies();
    const walletAddress = cookieStore.get("wallet-address")?.value;

    if (!walletAddress) {
      return { user: null };
    }

    const userId = getUUIDFromWallet(walletAddress);

    // Check if user exists, if not create them
    const [existingUser] = await getUser(walletAddress);

    if (!existingUser) {
      // Create user with wallet address as email and a default password
      await createUser(walletAddress, "default-password");
    }

    return {
      user: {
        id: userId,
        walletAddress: walletAddress,
        email: walletAddress,
      },
    };
  } catch (error) {
    console.error("Auth error:", error);
    return { user: null };
  }
}

export async function signIn(provider: string, credentials: any) {
  return true;
}

export async function signOut() {
  return true;
}
