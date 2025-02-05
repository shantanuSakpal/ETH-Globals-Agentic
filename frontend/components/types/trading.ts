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
  
  export interface TradingFormData {
    collateralAmount: number
    selectedCollateral: string
    loopMultiplier: number
    synthAmount: number
    selectedSynth: string
    slippageTolerance: number
  }
  
  export interface SummaryData {
    estimatedApy: number
    yourLoop: number
    totalDeposited: number
    totalSynthBorrowed: number
    synthBalanceFee: number
  }
  
  