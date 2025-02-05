// frontend/lib/context/wallet-context.tsx
'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useWallets } from '@privy-io/react-auth';

interface WalletContextType {
  walletAddress: string | null;
}

const WalletContext = createContext<WalletContextType>({ walletAddress: null });

export function WalletProvider({ children }: { children: ReactNode }) {
  const { wallets } = useWallets();
  const walletAddress = wallets[0]?.address || null;

  return (
    <WalletContext.Provider value={{ walletAddress }}>
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  return useContext(WalletContext);
}