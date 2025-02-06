import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { SummaryData } from "@/components/types/trading";
import useWebSocket from "@/lib/websocket/useWebSocket"; // Import WebSocket hook

interface SummaryProps {
  data: SummaryData;
  isLoading?: boolean;
}

export function Summary({ data, isLoading }: SummaryProps) {
  const { sendMessage } = useWebSocket("ws://localhost:8000/ws"); // WebSocket connection

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;

  const handleConfirm = () => {
    // Ensure the client is identifiable (e.g., generate an ID or use a session)
    const clientId = "frontend-user"; // Replace with actual user ID if available

    // Prepare WebSocket message format
    const formattedMessage = {
      client: clientId,
      content: JSON.stringify({
        estimatedApy: data.estimatedApy,
        yourLoop: data.yourLoop,
        totalDeposited: data.totalDeposited,
        totalSynthBorrowed: data.totalSynthBorrowed,
        synthBalanceFee: data.synthBalanceFee,
      }),
      timestamp: new Date().toISOString(),
    };

    sendMessage(JSON.stringify(formattedMessage)); // Send structured message
    console.log("Sent to WebSocket:", formattedMessage); // Debugging
  };

  return (
    <Card className="border bg-background">
      <CardHeader>
        <CardTitle className="text-xl font-medium">Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Estimated APY</p>
            <p className="text-lg font-medium">
              {data.estimatedApy ? `${data.estimatedApy}%` : "-"}
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Your Loop</p>
            <p className="text-lg font-medium">{data.yourLoop.toFixed(2)}x</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total deposited</span>
            <span>
              {formatCurrency(data.totalDeposited)} →{" "}
              {formatCurrency(data.totalDeposited)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total synth borrowed</span>
            <span>
              {formatCurrency(data.totalSynthBorrowed)} →{" "}
              {formatCurrency(data.totalSynthBorrowed)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Synth balance fee</span>
            <span>
              {data.synthBalanceFee ? `${data.synthBalanceFee}%` : "-"}
            </span>
          </div>
        </div>

        <Button className="w-full" onClick={handleConfirm} disabled={isLoading}>
          Confirm
        </Button>
      </CardContent>
    </Card>
  );
}
