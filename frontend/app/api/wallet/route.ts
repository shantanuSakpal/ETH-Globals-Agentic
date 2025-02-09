import { NextResponse } from 'next/server';
import { privyServer } from '@/lib/privy/privy-server';

export async function POST(req: Request) {
  try {
    // Validate the request body first
    const body = await req.json().catch(() => null);
    if (!body) {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    const { action, message, recipient, amount, walletId } = body;

    if (!action) {
      return NextResponse.json({ error: 'Action is required' }, { status: 400 });
    }

    switch (action) {
      case 'create':
        try {
          const wallet = await privyServer.walletApi.create({
            chainType: 'ethereum'
          });
          return NextResponse.json(wallet);
        } catch (error) {
          console.error('Privy wallet creation error:', error);
          return NextResponse.json(
            { error: 'Failed to create wallet' },
            { status: 500 }
          );
        }

      case 'sign':
        if (!message || !recipient) {
          return NextResponse.json(
            { error: 'Missing message or recipient' },
            { status: 400 }
          );
        }
        try {
          const signedMessage = await privyServer.walletApi.ethereum.signMessage({
            walletId: recipient,
            message: message
          });
          return NextResponse.json(signedMessage);
        } catch (error) {
          console.error('Signing error:', error);
          return NextResponse.json(
            { error: 'Failed to sign message' },
            { status: 500 }
          );
        }

      case 'send':
        if (!walletId || !recipient || !amount) {
          return NextResponse.json(
            { error: 'Missing walletId, recipient, or amount' },
            { status: 400 }
          );
        }
        try {
          const tx = await privyServer.walletApi.ethereum.sendTransaction({
            walletId: walletId,
            caip2: 'eip155:84532',
            transaction: {
              to: recipient,
              value: amount,
              chainId: 84532
            },
          });
          return NextResponse.json(tx);
        } catch (error) {
          console.error('Transaction error:', error);
          return NextResponse.json(
            { error: 'Failed to send transaction' },
            { status: 500 }
          );
        }

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Wallet API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}