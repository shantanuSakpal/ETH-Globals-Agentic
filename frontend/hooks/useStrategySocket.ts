import { useEffect, useRef } from 'react';

export type MessageData = {
  type: string;
  data: any;
};

export function useStrategySocket(onMessage: (msg: MessageData) => void) {
  const ws = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    // Ensure the token is passed as a query parameter.
    const userToken = process.env.NEXT_PUBLIC_AUTH_TOKEN || 'your_user_token'; // Replace with the actual token logic
    // Use env variable or fallback to localhost
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/strategy';
    ws.current = new WebSocket(wsUrl);
    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };
    ws.current.onmessage = (event) => {
      try {
        const msg: MessageData = JSON.parse(event.data);
        onMessage(msg);
      } catch (error) {
        console.error('Error parsing message', error);
      }
    };
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
    return () => {
      ws.current?.close();
    };
  }, [onMessage]);
  
  const sendMessage = (msg: MessageData) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(msg));
    } else {
      console.error('WebSocket not connected');
    }
  };

  return { sendMessage };
}