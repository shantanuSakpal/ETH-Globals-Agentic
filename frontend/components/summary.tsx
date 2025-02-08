import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { ETHLoopSummaryData } from "@/components/types/trading";

interface SummaryProps {
  data: ETHLoopSummaryData;
  onConfirm: () => void;
  isLoading?: boolean;
}

export function Summary({ data, onConfirm, isLoading }: SummaryProps) {
  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  const formatPercent = (value: number) => `${value.toFixed(2)}%`;

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Low":
        return "text-green-500";
      case "Medium":
        return "text-yellow-500";
      case "High":
        return "text-red-500";
      default:
        return "";
    }
  };

  return (
    <Card className="border bg-background">
      <CardHeader>
        <CardTitle className="text-xl font-medium">Position Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Estimated APY</p>
            <p className="text-lg font-medium">
              {formatPercent(data.estimatedApy)}
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Current Leverage</p>
            <p className="text-lg font-medium">{data.leverage.toFixed(2)}x</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total ETH Deposited</span>
            <span>{data.totalDeposited.toFixed(4)} ETH</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total USDC Borrowed</span>
            <span>{formatCurrency(data.totalBorrowed)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Health Factor</span>
            <span>{data.healthFactor.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Risk Level</span>
            <span className={getRiskColor(data.riskLevel)}>
              {data.riskLevel}
            </span>
          </div>
        </div>

        <Button className="w-full" onClick={onConfirm} disabled={isLoading}>
          {isLoading ? "Initializing..." : "Initialize Strategy"}
        </Button>
      </CardContent>
    </Card>
  );
}
