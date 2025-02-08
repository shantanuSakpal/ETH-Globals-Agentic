'use client';

import { PrivyProvider } from '@privy-io/react-auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

// This component handles the authentication check
function AuthCheck({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  return <>{children}</>;
}

export function Provider({ children }: { children: React.ReactNode }) {
  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID!}
      config={{
        loginMethods: ['wallet', 'email', 'google', 'twitter'],
        appearance: {
          theme: 'dark',
          accentColor: '#676FFF',
          showWalletLoginFirst: true,
        },
          
      }}
    >
      <AuthCheck>{children}</AuthCheck>
    </PrivyProvider>
  );
}