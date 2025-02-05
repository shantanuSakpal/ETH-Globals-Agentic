"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { COLLATERAL_OPTIONS, SYNTH_OPTIONS, SLIPPAGE_OPTIONS } from "@/lib/constant"
import type { TradingFormData } from "@/components/types/trading"

interface TradingFormProps {
  onChange: (data: TradingFormData) => void
  data: TradingFormData
}

export function TradingForm({ onChange, data }: TradingFormProps) {
  return (
    <div className="space-y-6">
      <Card className="border bg-background">
        <CardHeader>
          <CardTitle className="text-xl font-medium">Supply collateral</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Input
              type="number"
              value={data.collateralAmount || ""}
              onChange={(e) => onChange({ ...data, collateralAmount: Number.parseFloat(e.target.value) || 0 })}
              className="bg-background border"
              placeholder="0"
            />
            <Select
              value={data.selectedCollateral}
              onValueChange={(value) => onChange({ ...data, selectedCollateral: value })}
            >
              <SelectTrigger className="w-[180px] bg-background border">
                <SelectValue placeholder="Choose collateral" />
              </SelectTrigger>
              <SelectContent>
                {COLLATERAL_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label} ({option.chain})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">≈$0.00</p>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <Label className="text-muted-foreground">Set Loop</Label>
        <Slider
          value={[data.loopMultiplier]}
          onValueChange={([value]) => onChange({ ...data, loopMultiplier: value })}
          min={1}
          max={10}
          step={0.1}
          className="py-4"
        />
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>1x</span>
          <span>10x</span>
        </div>
      </div>

      <Card className="border bg-background">
        <CardHeader>
          <CardTitle className="text-xl font-medium">Borrow Synth</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Input
              type="number"
              value={data.synthAmount || ""}
              onChange={(e) => onChange({ ...data, synthAmount: Number.parseFloat(e.target.value) || 0 })}
              className="bg-background border"
              placeholder="0.0000"
            />
            <Select value={data.selectedSynth} onValueChange={(value) => onChange({ ...data, selectedSynth: value })}>
              <SelectTrigger className="w-[180px] bg-background border">
                <SelectValue placeholder="Choose synth" />
              </SelectTrigger>
              <SelectContent>
                {SYNTH_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">≈$0.00</p>
          <p className="mt-1 text-sm text-muted-foreground">Max: 0.0000</p>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Label className="text-muted-foreground">Slippage tolerance</Label>
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

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Synth Limit</span>
            <span>0 → 0.0%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Health Factor</span>
            <span>0 → 0</span>
          </div>
        </div>
      </div>
    </div>
  )
}

