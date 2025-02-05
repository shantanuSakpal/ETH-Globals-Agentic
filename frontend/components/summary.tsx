import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { SummaryData } from "@/components/types/trading"

interface SummaryProps {
  data: SummaryData
  onConfirm: () => void
  isLoading?: boolean
}

export function Summary({ data, onConfirm, isLoading }: SummaryProps) {
  const formatCurrency = (value: number) => `$${value.toFixed(2)}`

  return (
    <Card className="border bg-background">
      <CardHeader>
        <CardTitle className="text-xl font-medium">Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Estimated APY</p>
            <p className="text-lg font-medium">{data.estimatedApy ? `${data.estimatedApy}%` : "-"}</p>
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
              {formatCurrency(data.totalDeposited)} → {formatCurrency(data.totalDeposited)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total synth borrowed</span>
            <span>
              {formatCurrency(data.totalSynthBorrowed)} → {formatCurrency(data.totalSynthBorrowed)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Synth balance fee</span>
            <span>{data.synthBalanceFee ? `${data.synthBalanceFee}%` : "-"}</span>
          </div>
        </div>

        <Button className="w-full" onClick={onConfirm} disabled={isLoading}>
          Confirm
        </Button>
      </CardContent>
    </Card>
  )
}

