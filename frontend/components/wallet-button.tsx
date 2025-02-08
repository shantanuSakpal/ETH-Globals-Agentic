"use client";
import { useConnectWallet, useWallets } from '@privy-io/react-auth';
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export default function WalletButton() {
  const { connectWallet } = useConnectWallet();
  const { ready, wallets } = useWallets();
  const wallet = wallets[0];

  // Show loading state while the hook is initializing
  if (!ready) {
    return (
      <Button size="lg" disabled>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Connecting...
      </Button>
    );
  }

  // If there's a connected wallet, show the wallet address
  if (wallet) {
    const shortAddress = `${wallet.address.slice(0, 6)}...${wallet.address.slice(-4)}`;
    
    return (
      <Button 
        size="lg"
        variant="outline"
        onClick={() => wallet.loginOrLink()}
      >
        {shortAddress}
      </Button>
    );
  }

  // Default state - not connected
  return (
    <Button 
      onClick={connectWallet} 
      size="lg"
    >
      Connect Wallet
    </Button>
  );
}