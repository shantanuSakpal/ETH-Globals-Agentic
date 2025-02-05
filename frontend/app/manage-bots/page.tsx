"use client"

import { useState } from "react"
import { TradingForm } from "@/components/trading-form"
import { Summary } from "@/components/summary"
import type { TradingFormData, SummaryData } from "@/components/types/trading"

const initialFormData: TradingFormData = {
  collateralAmount: 0,
  selectedCollateral: "",
  loopMultiplier: 1,
  synthAmount: 0,
  selectedSynth: "",
  slippageTolerance: 0.5,
}

const initialSummaryData: SummaryData = {
  estimatedApy: 0,
  yourLoop: 1,
  totalDeposited: 0,
  totalSynthBorrowed: 0,
  synthBalanceFee: 0,
}

export default function TradingPage() {
  const [formData, setFormData] = useState<TradingFormData>(initialFormData)
  const [summaryData, setSummaryData] = useState<SummaryData>(initialSummaryData)
  const [isLoading, setIsLoading] = useState(false)

  const handleFormChange = (newData: TradingFormData) => {
    setFormData(newData)
    setSummaryData({
      ...summaryData,
      yourLoop: newData.loopMultiplier,
      totalDeposited: newData.collateralAmount,
      totalSynthBorrowed: newData.synthAmount,
    })
  }

  const handleConfirm = async () => {
    setIsLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      console.log("Confirmed:", formData)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="container mx-auto px-4  py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 ml-[10%] max-w-full mx-auto">
          <TradingForm data={formData} onChange={handleFormChange} />
           <Summary data={summaryData} onConfirm={handleConfirm} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}
