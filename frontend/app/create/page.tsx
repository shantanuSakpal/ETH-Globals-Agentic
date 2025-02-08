"use client"

import { useState } from "react"
import { TradingForm } from "@/components/trading-form"
import { Summary } from "@/components/summary"
import type { ETHLoopFormData, ETHLoopSummaryData } from "@/components/types/trading"
import { useStrategySocket } from "@/hooks/useStrategySocket"

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
  const [vaultId, setVaultId] = useState<string | null>(null)
  const [depositAddress, setDepositAddress] = useState<string | null>(null)
  const [instruction, setInstruction] = useState<string>("")

  const { sendMessage } = useStrategySocket((msg) => {
    if (msg.type === "strategy_init") {
      // Received when the backend creates the vault and initializes the agent.
      setVaultId(msg.data.vault_id)
      setDepositAddress(msg.data.deposit_address)
      setInstruction("Strategy initialized. Please fund your agent wallet with gas to continue.")
    } else if (msg.type === "deposit_complete") {
      setInstruction("Deposit complete. Vault contract deployed successfully.")
    } else if (msg.type === "monitor_update") {
      // Optionally update UI with monitoring updates.
      console.log("Monitor update:", msg.data)
    }
  })

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

  //const handleConfirm = async () => {
  const handleStrategyInit = () => {
    setIsLoading(true)
    // try {
    //   const response = await fetch('/api/strategy/eth-loop', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(formData)
    //   })
      
    //   if (!response.ok) {
    //     throw new Error('Failed to initialize strategy')
    //   }
    //   console.log('Strategy initialized successfully')
    // } catch (error) {
    //   console.error('Error:', error)
    // } finally {
    //   setIsLoading(false)
    // }
    // Send WS message to initialize strategy (creates vault and agent)
    sendMessage({
      type: "strategy_select",
      data: {
        strategy_id: "eth-usdc-loop",
        initial_deposit: formData.collateralAmount,
        parameters: formData,
      }
    })
    setIsLoading(false)
  }

  const handleConfirmDeposit = () => {
    if (!vaultId) return
    // Send WS message to proceed with the deposit and vault contract deployment.
    sendMessage({
      type: "deposit",
      data: {
        vault_id: vaultId,
        // Additional deposit parameters can be added here.
      }
    })
  }
  
  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 ml-[10%] max-w-full mx-auto">
          <TradingForm data={formData} onChange={handleFormChange} />
          {/* <Summary data={summaryData} onConfirm={handleConfirm} isLoading={isLoading} /> */}
          <Summary data={summaryData} onConfirm={handleStrategyInit} isLoading={isLoading} />
        </div>
        {instruction && 
          <div className="mt-8 text-center">
            <p>{instruction}</p>
            {vaultId && !depositAddress && (
              <button onClick={handleConfirmDeposit} className="btn-primary mt-4">
                Confirm Deposit
              </button>
            )}
            {depositAddress && (
              <p>Your deposit address: {depositAddress}</p>
            )}
          </div>
        }
      </div>
    </div>
  )
}