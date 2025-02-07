"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { COLLATERAL_OPTIONS, SLIPPAGE_OPTIONS } from "@/lib/constant"
import type { ETHLoopFormData } from "@/components/types/trading"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { InfoCircledIcon } from "@radix-ui/react-icons"

interface TradingFormProps {
  onChange: (data: ETHLoopFormData) => void
  data: ETHLoopFormData
}

export function TradingForm({ onChange, data }: TradingFormProps) {
  return (
    <div className="space-y-6">
      <Card className="border bg-background">
        <CardHeader>
          <CardTitle className="text-xl font-medium">ETH Collateral</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Input
              type="number"
              value={data.collateralAmount || ""}
              onChange={(e) => onChange({ ...data, collateralAmount: Number(e.target.value) || 0 })}
              className="bg-background border"
              placeholder="0"
              min={0.1}
              step={0.1}
            />
            <span className="text-sm font-medium">ETH</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">Min: 0.1 ETH</p>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Label className="text-muted-foreground">Maximum Leverage</Label>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <InfoCircledIcon className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Higher leverage means higher potential returns but also higher risk</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <Slider
          value={[data.maxLeverage]}
          onValueChange={([value]) => onChange({ ...data, maxLeverage: value })}
          min={1}
          max={3}
          step={0.1}
          className="py-4"
        />
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>1x</span>
          <span>3x</span>
        </div>
      </div>

      <Card className="border bg-background">
        <CardHeader>
          <CardTitle className="text-xl font-medium">Strategy Parameters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Target APY (%)</Label>
            <Input
              type="number"
              value={data.targetApy || ""}
              onChange={(e) => onChange({ ...data, targetApy: Number.parseFloat(e.target.value) || 0 })}
              className="mt-2"
              placeholder="10.0"
              min={0}
              max={100}
              step={0.1}
            />
          </div>
          
          <div>
            <Label>Minimum Collateral Ratio</Label>
            <Input
              type="number"
              value={data.minCollateralRatio || ""}
              onChange={(e) => onChange({ ...data, minCollateralRatio: Number.parseFloat(e.target.value) || 0 })}
              className="mt-2"
              placeholder="1.5"
              min={1.1}
              max={2}
              step={0.1}
            />
          </div>

          <div>
            <Label>Rebalance Threshold (%)</Label>
            <Input
              type="number"
              value={data.rebalanceThreshold || ""}
              onChange={(e) => onChange({ ...data, rebalanceThreshold: Number.parseFloat(e.target.value) || 0 })}
              className="mt-2"
              placeholder="5.0"
              min={1}
              max={20}
              step={0.5}
            />
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Label className="text-muted-foreground">Slippage Tolerance</Label>
          <Select
            value={data.slippageTolerance.toString()}
            onValueChange={(value) => onChange({ ...data, slippageTolerance: Number.parseFloat(value) })}
          >
            <SelectTrigger className="w-[100px] bg-background border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {SLIPPAGE_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value.toString()}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )
}
