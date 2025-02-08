import { useState, useEffect, useCallback } from "react";

const useWebSocket = (url: string) => {
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(url);

    socket.onopen = () => console.log("Connected to WebSocket server");

    socket.onmessage = (event: MessageEvent) => {
      console.log("Received WebSocket Message:", event.data);
    };

    socket.onclose = () => console.log("Disconnected from WebSocket server");

    setWs(socket);

    return () => {
      socket.close();
    };
  }, [url]);

  const sendMessage = useCallback(
    (message: string) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(message);
      } else {
        console.error("WebSocket is not open. Unable to send message.");
      }
    },
    [ws]
  );

  return { sendMessage };
};

export default useWebSocket;
