"use client"

import { Switch } from "@/components/ui/switch"
import { Line, LineChart, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {useRouter} from "next/navigation"
// Define the bot type to match your data structure
interface Bot {
  id: number
  pair: string
  profitGained: string
  percentageGain: string
  workingTime: string
  status: string
  totalBalance: string
  orders: string
  isActive: boolean
  data: Array<{ value: number }>
}

// Update BotCard to accept children and className props
interface BotCardProps {
  children: React.ReactNode
  className?: string
}

function BotCard({ children, className = "" }: BotCardProps) {
  return (
    <Card className={className}>
      {children}
    </Card>
  )
}

const data = [
  { value: 100 },
  { value: 120 },
  { value: 110 },
  { value: 130 },
  { value: 125 },
  { value: 140 },
  { value: 135 },
]

const bots: Bot[] = [
  {
    id: 1,
    pair: "ETH/USDT",
    profitGained: "34.12%",
    percentageGain: "14.16%",
    workingTime: "9h 23m",
    status: "Active",
    totalBalance: "$4,308.12",
    orders: "36",
    isActive: true,
    data: [...data],
  },
  {
    id: 2,
    pair: "ETH/BTC",
    profitGained: "23.26%",
    percentageGain: "12.45%",
    workingTime: "1h 12m",
    status: "Active",
    totalBalance: "$1,224.51",
    orders: "16",
    isActive: true,
    data: [...data.map((d) => ({ value: d.value * 0.8 }))],
  },
  {
    id: 3,
    pair: "ETH/USDC",
    profitGained: "0%",
    percentageGain: "0%",
    workingTime: "0m",
    status: "Inactive",
    totalBalance: "$0",
    orders: "0",
    isActive: false,
    data: [...data.map((d) => ({ value: d.value * 0.5 }))],
  },
]

export default function TradingBots() {
  const router = useRouter();

  return (
    <div className="min-w-full bg-black text-white p-6">
      <div className="mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-semibold">AI Trading Strategies</h1>
          <Button
            onClick={() => router.push("/create")}
            className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto"
          >
            + Add Strategy
          </Button> 
        </div>

        <div className="space-y-4">
          {bots.map((bot) => (
            <BotCard key={bot.id} className="bg-zinc-900/50 border-zinc-800">
              <div className="p-6">
                <div className="grid grid-cols-12 gap-6">
                  {/* Trading Pair and Chart */}
                  <div className="col-span-3">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex -space-x-1">
                        <div className="w-6 h-6 rounded-full bg-blue-500" />
                        <div className="w-6 h-6 rounded-full bg-green-500" />
                      </div>
                      <span className="font-medium">{bot.pair}</span>
                    </div>
                    <div className="h-[60px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={bot.data}>
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke={bot.isActive ? "#22c55e" : "#ef4444"}
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="col-span-7 grid grid-cols-4 gap-6">
                    <div>
                      <p className="text-zinc-400 text-sm mb-1">Profit gained</p>
                      <p className="text-lg font-medium text-green-500">{bot.profitGained}</p>
                      <p className="text-sm text-red-500">{bot.percentageGain}</p>
                    </div>
                    <div>
                      <p className="text-zinc-400 text-sm mb-1">Working time</p>
                      <p className="text-lg font-medium">{bot.workingTime}</p>
                      <p className="text-sm text-zinc-400">{bot.status}</p>
                    </div>
                    <div>
                      <p className="text-zinc-400 text-sm mb-1">Total Balance</p>
                      <p className="text-lg font-medium">{bot.totalBalance}</p>
                      <p className="text-sm text-zinc-400">Orders: {bot.orders}</p>
                    </div>
                    <div>
                      <p className="text-zinc-400 text-sm mb-1">Exchange</p>
                      <div className="flex gap-1">
                        <div className="w-6 h-6 rounded-full bg-blue-500" />
                        <div className="w-6 h-6 rounded-full bg-purple-500" />
                        <div className="w-6 h-6 rounded-full bg-orange-500" />
                      </div>
                    </div>
                  </div>

                  {/* Toggle Switch */}
                  <div className="col-span-2 flex justify-end items-start">
                    <Switch
                      checked={bot.isActive}
                      onCheckedChange={(checked) => {
                        // Handle state change here
                      }}
                    />
                  </div>
                </div>
              </div>
            </BotCard>
          ))}
        </div>
      </div>
    </div>
  )
}