from decimal import Decimal

# Protocol Constants
MAX_LEVERAGE = Decimal('5.0')  # Maximum leverage allowed
MIN_COLLATERAL_RATIO = Decimal('1.1')  # Minimum collateral ratio
LIQUIDATION_THRESHOLD = Decimal('0.8')  # Liquidation threshold
MAX_UTILIZATION = Decimal('0.95')  # Maximum pool utilization

# Fee Constants
BORROW_FEE = Decimal('0.001')  # 0.1% borrow fee
REPAY_FEE = Decimal('0.0005')  # 0.05% repay fee
LIQUIDATION_FEE = Decimal('0.05')  # 5% liquidation fee
FLASH_LOAN_FEE = Decimal('0.0009')  # 0.09% flash loan fee

# Time Constants
MIN_LOCK_TIME = 60  # Minimum lock time in seconds
MAX_LOCK_TIME = 365 * 24 * 60 * 60  # Maximum lock time (1 year) in seconds
REBALANCE_INTERVAL = 3600  # Minimum time between rebalances in seconds

# Position Constants
MIN_POSITION_SIZE = Decimal('0.1')  # Minimum position size in ETH
MAX_POSITION_SIZE = Decimal('1000')  # Maximum position size in ETH
MIN_DEBT_SIZE = Decimal('100')  # Minimum debt size in USDC

# Market Constants
SUPPORTED_COLLATERAL = [
    'ETH',
    'wstETH',
    'rETH',
    'cbETH'
]

SUPPORTED_DEBT = [
    'USDC',
    'USDT',
    'DAI'
]

# Contract Addresses (Mainnet)
ADDRESSES = {
    'MORPHO_CORE': '0x...',  # Add actual address
    'MORPHO_LENS': '0x...',  # Add actual address
    'PRICE_ORACLE': '0x...',  # Add actual address
    'REWARDS': '0x...',  # Add actual address
    
    # Token Addresses
    'ETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'wstETH': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
    'rETH': '0xae78736Cd615f374D3085123A210448E74Fc6393',
    'cbETH': '0xBe9895146f7AF43049ca1c1AE358B0541Ea49704'
}

# Error Messages
ERRORS = {
    'INSUFFICIENT_COLLATERAL': 'Insufficient collateral for the requested action',
    'EXCEEDS_MAX_LEVERAGE': 'Requested leverage exceeds maximum allowed',
    'BELOW_MIN_COLLATERAL_RATIO': 'Action would put position below minimum collateral ratio',
    'UNSUPPORTED_COLLATERAL': 'Unsupported collateral token',
    'UNSUPPORTED_DEBT': 'Unsupported debt token',
    'POSITION_TOO_SMALL': 'Position size below minimum allowed',
    'POSITION_TOO_LARGE': 'Position size exceeds maximum allowed',
    'INSUFFICIENT_LIQUIDITY': 'Insufficient liquidity in the pool',
    'MARKET_PAUSED': 'Market is currently paused',
    'INVALID_AMOUNT': 'Invalid amount specified',
    'UNAUTHORIZED': 'Unauthorized to perform this action',
    'POSITION_NOT_FOUND': 'Position not found',
    'FLASH_LOAN_FAILED': 'Flash loan execution failed'
}

# Event Names
EVENTS = {
    'POSITION_OPENED': 'PositionOpened',
    'POSITION_CLOSED': 'PositionClosed',
    'POSITION_ADJUSTED': 'PositionAdjusted',
    'COLLATERAL_ADDED': 'CollateralAdded',
    'COLLATERAL_REMOVED': 'CollateralRemoved',
    'DEBT_INCREASED': 'DebtIncreased',
    'DEBT_DECREASED': 'DebtDecreased',
    'LIQUIDATION': 'Liquidation',
    'FLASH_LOAN': 'FlashLoan',
    'REWARDS_CLAIMED': 'RewardsClaimed'
} 