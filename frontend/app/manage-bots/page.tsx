"use client"

import { useState } from "react"
import { TradingForm } from "@/components/trading-form"
import { Summary } from "@/components/summary"
import type { ETHLoopFormData, ETHLoopSummaryData } from "@/components/types/trading"

const initialFormData: ETHLoopFormData = {
  collateralAmount: 0,
  maxLeverage: 3.0,
  minCollateralRatio: 1.5,
  targetApy: 10.0,
  rebalanceThreshold: 5.0,
  slippageTolerance: 0.5,
  riskLevel: 'Low'
}

const initialSummaryData: ETHLoopSummaryData = {
  estimatedApy: 0,
  leverage: 1,
  totalDeposited: 0,
  totalBorrowed: 0,
  healthFactor: 0,
  riskLevel: 'Low'
}

export default function TradingPage() {
  const [formData, setFormData] = useState<ETHLoopFormData>(initialFormData)
  const [summaryData, setSummaryData] = useState<ETHLoopSummaryData>(initialSummaryData)
  const [isLoading, setIsLoading] = useState(false)

  const calculateSummaryData = (data: ETHLoopFormData): ETHLoopSummaryData => {
    const totalDeposited = data.collateralAmount
    const leverage = data.maxLeverage
    const totalBorrowed = totalDeposited * (leverage - 1) * 2000 // Assuming ETH price of $2000
    const healthFactor = data.minCollateralRatio
    const estimatedApy = data.targetApy * leverage
    
    let riskLevel: 'Low' | 'Medium' | 'High'
    if (leverage <= 1.5) riskLevel = 'Low'
    else if (leverage <= 2.5) riskLevel = 'Medium'
    else riskLevel = 'High'

    return {
      estimatedApy,
      leverage,
      totalDeposited,
      totalBorrowed,
      healthFactor,
      riskLevel
    }
  }

  const handleFormChange = (newData: ETHLoopFormData) => {
    setFormData(newData)
    setSummaryData(calculateSummaryData(newData))
  }

  const handleConfirm = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/strategy/eth-loop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to initialize strategy')
      }
      console.log('Strategy initialized successfully')
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 ml-[10%] max-w-full mx-auto">
          <TradingForm data={formData} onChange={handleFormChange} />
          <Summary data={summaryData} onConfirm={handleConfirm} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}
