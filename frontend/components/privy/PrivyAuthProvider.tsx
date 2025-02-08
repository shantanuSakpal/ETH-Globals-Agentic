'use client';

import { PrivyProvider } from '@privy-io/react-auth';
import { ReactNode } from 'react';
import { WalletProvider } from '@/lib/privy/wallet-context';

export function PrivyAuthProvider({ children }: { children: ReactNode }) {
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
      <WalletProvider>
        {children}
      </WalletProvider>
    </PrivyProvider>
  );
}