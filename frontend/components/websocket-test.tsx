// 'use client';

// import { useEffect, useState, useCallback } from 'react';
// import { useSession } from 'next-auth/react';

// interface WebSocketMessage {
//   type: string;
//   data: any;
//   timestamp: string;
// }

// export default function WebSocketTest() {
//   const { data: session } = useSession();
//   const [socket, setSocket] = useState<WebSocket | null>(null);
//   const [messages, setMessages] = useState<WebSocketMessage[]>([]);
//   const [connected, setConnected] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   // Initialize WebSocket connection
//   useEffect(() => {
//     if (!session?.accessToken) return;

//     const ws = new WebSocket(
//       `ws://localhost:8000/ws?token=${session.accessToken}`
//     );

//     ws.onopen = () => {
//       console.log('Connected to WebSocket');
//       setConnected(true);
//       setError(null);

//       // Subscribe to market updates
//       ws.send(JSON.stringify({
//         type: 'subscribe',
//         data: {
//           topics: ['market_ETH-USDC']
//         },
//         timestamp: new Date().toISOString()
//       }));
//     };

//     ws.onmessage = (event) => {
//       const message = JSON.parse(event.data);
//       setMessages((prev) => [...prev, message].slice(-10)); // Keep last 10 messages
//     };

//     ws.onerror = (event) => {
//       console.error('WebSocket error:', event);
//       setError('WebSocket error occurred');
//     };

//     ws.onclose = () => {
//       console.log('WebSocket closed');
//       setConnected(false);
//     };

//     setSocket(ws);

//     return () => {
//       ws.close();
//     };
//   }, [session?.accessToken]);

//   // Create strategy handler
//   const handleCreateStrategy = useCallback(() => {
//     if (!socket || socket.readyState !== WebSocket.OPEN) return;

//     const strategyParams = {
//       strategy_id: 'eth-usdc-loop',
//       name: 'ETH-USDC Loop Strategy',
//       description: 'Test strategy',
//       risk_level: 'medium',
//       target_apy: 10.0,
//       max_leverage: 2.0,
//       rebalance_threshold: 5.0,
//       initial_capital: 1000.0,
//       asset_pair: 'ETH-USDC'
//     };

//     socket.send(JSON.stringify({
//       type: 'strategy_select',
//       data: strategyParams,
//       timestamp: new Date().toISOString()
//     }));
//   }, [socket]);

//   return (
//     <div className="p-4">
//       <h2 className="text-2xl font-bold mb-4">WebSocket Test</h2>

//       {/* Connection Status */}
//       <div className="mb-4">
//         <p className="font-semibold">
//           Status:{' '}
//           <span
//             className={`${
//               connected ? 'text-green-500' : 'text-red-500'
//             }`}
//           >
//             {connected ? 'Connected' : 'Disconnected'}
//           </span>
//         </p>
//         {error && (
//           <p className="text-red-500 mt-2">{error}</p>
//         )}
//       </div>

//       {/* Actions */}
//       <div className="mb-4">
//         <button
//           onClick={handleCreateStrategy}
//           disabled={!connected}
//           className={`px-4 py-2 rounded ${
//             connected
//               ? 'bg-blue-500 hover:bg-blue-600 text-white'
//               : 'bg-gray-300 text-gray-500 cursor-not-allowed'
//           }`}
//         >
//           Create Test Strategy
//         </button>
//       </div>

//       {/* Messages */}
//       <div className="mt-8">
//         <h3 className="text-xl font-semibold mb-2">Recent Messages</h3>
//         <div className="space-y-2">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className="p-3 bg-gray-100 rounded"
//             >
//               <p className="font-mono text-sm">
//                 <span className="font-semibold">Type:</span> {msg.type}
//               </p>
//               <p className="font-mono text-sm">
//                 <span className="font-semibold">Data:</span>{' '}
//                 {JSON.stringify(msg.data)}
//               </p>
//               <p className="font-mono text-sm text-gray-500">
//                 {new Date(msg.timestamp).toLocaleString()}
//               </p>
//             </div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// } 