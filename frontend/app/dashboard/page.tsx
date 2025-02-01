"use client"
import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { ArrowUpRight, ArrowDownRight, DollarSign, Bitcoin } from 'lucide-react';

// Extended sample data
const tradingData = [
  { name: 'Jan', btc: 45000, eth: 3200, sol: 140, volume: 12500 },
  { name: 'Feb', btc: 47000, eth: 3400, sol: 155, volume: 13200 },
  { name: 'Mar', btc: 42000, eth: 3100, sol: 130, volume: 11800 },
  { name: 'Apr', btc: 49000, eth: 3600, sol: 165, volume: 14500 },
  { name: 'May', btc: 51000, eth: 3800, sol: 180, volume: 15200 },
  { name: 'Jun', btc: 48000, eth: 3500, sol: 170, volume: 13800 },
  { name: 'Jul', btc: 52000, eth: 3900, sol: 190, volume: 16000 },
  { name: 'Aug', btc: 53000, eth: 4000, sol: 200, volume: 16500 },
  { name: 'Sep', btc: 50000, eth: 3700, sol: 175, volume: 14800 },
  { name: 'Oct', btc: 54000, eth: 4100, sol: 210, volume: 17000 },
  { name: 'Nov', btc: 55000, eth: 4200, sol: 220, volume: 17500 },
  { name: 'Dec', btc: 56000, eth: 4300, sol: 230, volume: 18000 },
];

const recentTrades = [
  { id: 1, pair: 'BTC/USDT', type: 'Buy', amount: '0.25', price: '48,235.50', total: '12,058.87', time: '2 min ago' },
  { id: 2, pair: 'ETH/USDT', type: 'Sell', amount: '3.50', price: '3,521.20', total: '12,324.20', time: '5 min ago' },
  { id: 3, pair: 'SOL/USDT', type: 'Buy', amount: '20.00', price: '180.30', total: '3,606.00', time: '8 min ago' },
  { id: 4, pair: 'BTC/USDT', type: 'Buy', amount: '0.15', price: '48,240.30', total: '7,236.04', time: '10 min ago' },
  { id: 5, pair: 'ETH/USDT', type: 'Buy', amount: '1.75', price: '3,522.50', total: '6,164.37', time: '15 min ago' },
  { id: 6, pair: 'SOL/USDT', type: 'Sell', amount: '15.00', price: '182.40', total: '2,736.00', time: '18 min ago' },
  { id: 7, pair: 'BTC/USDT', type: 'Sell', amount: '0.10', price: '48,236.70', total: '4,823.67', time: '20 min ago' },
  { id: 8, pair: 'ETH/USDT', type: 'Buy', amount: '2.25', price: '3,523.80', total: '7,928.55', time: '25 min ago' },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-white">Trading Dashboard</h1>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Trading Volume Card */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-300">Total Trading Volume</h3>
              <DollarSign className="h-4 w-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold mb-1 text-white">$2.4M</div>
            <div className="flex items-center text-sm text-green-400">
              <ArrowUpRight className="h-4 w-4 mr-1" />
              +12.5%
            </div>
          </div>
          
          {/* Active Traders Card */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-300">Active Traders</h3>
              <Bitcoin className="h-4 w-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold mb-1 text-white">1,234</div>
            <div className="flex items-center text-sm text-green-400">
              <ArrowUpRight className="h-4 w-4 mr-1" />
              +5.2%
            </div>
          </div>
          
          {/* BTC Price Card */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-300">BTC Price</h3>
              <Bitcoin className="h-4 w-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold mb-1 text-white">$48,235.50</div>
            <div className="flex items-center text-sm text-red-400">
              <ArrowDownRight className="h-4 w-4 mr-1" />
              -2.1%
            </div>
          </div>
          
          {/* 24h Volume Card */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-300">24h Volume</h3>
              <DollarSign className="h-4 w-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold mb-1 text-white">$425.2K</div>
            <div className="flex items-center text-sm text-green-400">
              <ArrowUpRight className="h-4 w-4 mr-1" />
              +8.1%
            </div>
          </div>
        </div>
        
        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          {/* Price Chart */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-white">Price Chart</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={tradingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#fff' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Line type="monotone" dataKey="btc" stroke="#3B82F6" />
                  <Line type="monotone" dataKey="eth" stroke="#8B5CF6" />
                  <Line type="monotone" dataKey="sol" stroke="#10B981" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Volume Chart */}
          <div className="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-white">Volume Analysis</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={tradingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#fff' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="volume" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        
        {/* Recent Trades Table */}
        <div className="bg-gray-800 rounded-lg shadow border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Recent Trades</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Pair</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Amount</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Price</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Total</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {recentTrades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-gray-700">
                    <td className="px-4 py-3 text-sm text-gray-300">{trade.pair}</td>
                    <td className={`px-4 py-3 text-sm ${
                      trade.type === 'Buy' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {trade.type}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-300">{trade.amount}</td>
                    <td className="px-4 py-3 text-sm text-gray-300">${trade.price}</td>
                    <td className="px-4 py-3 text-sm text-gray-300">${trade.total}</td>
                    <td className="px-4 py-3 text-sm text-gray-300">{trade.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}