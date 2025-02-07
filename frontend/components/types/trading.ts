export interface CollateralOption {
    value: string
    label: string
    chain: string
  }
  
  export interface SynthOption {
    value: string
    label: string
    maxAmount: number
  }
  
  export interface ETHLoopFormData {
    // Core Parameters
    collateralAmount: number
    maxLeverage: number
    minCollateralRatio: number
    targetApy: number
    rebalanceThreshold: number
    slippageTolerance: number
  }
  
  export interface ETHLoopSummaryData {
    estimatedApy: number
    leverage: number
    totalDeposited: number
    totalBorrowed: number
    healthFactor: number
    riskLevel: 'Low' | 'Medium' | 'High'
  }
  
  export interface TradingFormData {
    collateralAmount: number
    selectedCollateral: string
    loopMultiplier: number
    synthAmount: number
    selectedSynth: string
    slippageTolerance: number
    rebalanceThreshold: number
  }
  
  