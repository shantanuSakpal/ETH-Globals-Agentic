'use client';

import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useConnectWallet, useWallets } from '@privy-io/react-auth';
import { useEffect } from 'react';
import Cookies from 'js-cookie';

export function WalletConnectButton() {
  const { connectWallet } = useConnectWallet();
  const { ready, wallets } = useWallets();
  const wallet = wallets[0];
  
  useEffect(() => {
    if (wallet?.address) {
      Cookies.set('wallet-address', wallet.address, { path: '/' });
    } else {
      Cookies.remove('wallet-address');
    }
  }, [wallet?.address]);

  if (!ready) {
    return (
      <Button size="lg" disabled className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto">
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Connecting...
      </Button>
    );
  }

  if (wallet) {
    const shortAddress = `${wallet.address.slice(0, 6)}...${wallet.address.slice(-4)}`;
    return (
      <Button 
        size="lg"
        variant="outline"
        onClick={() => wallet.loginOrLink()}
        className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto"
      >
        {shortAddress}
      </Button>
    );
  }

  return (
    <Button 
      onClick={connectWallet} 
      size="lg"
      className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto"
    >
      Connect Wallet
    </Button>
  );
}