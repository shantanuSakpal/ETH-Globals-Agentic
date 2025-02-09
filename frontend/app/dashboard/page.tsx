"use client";
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Bitcoin,
} from "lucide-react";

// Extended sample data
const tradingData = [
  { name: "Jan", btc: 45000, eth: 3200, sol: 140, volume: 12500 },
  { name: "Feb", btc: 47000, eth: 3400, sol: 155, volume: 13200 },
  { name: "Mar", btc: 42000, eth: 3100, sol: 130, volume: 11800 },
  { name: "Apr", btc: 49000, eth: 3600, sol: 165, volume: 14500 },
  { name: "May", btc: 51000, eth: 3800, sol: 180, volume: 15200 },
  { name: "Jun", btc: 48000, eth: 3500, sol: 170, volume: 13800 },
  { name: "Jul", btc: 52000, eth: 3900, sol: 190, volume: 16000 },
  { name: "Aug", btc: 53000, eth: 4000, sol: 200, volume: 16500 },
  { name: "Sep", btc: 50000, eth: 3700, sol: 175, volume: 14800 },
  { name: "Oct", btc: 54000, eth: 4100, sol: 210, volume: 17000 },
  { name: "Nov", btc: 55000, eth: 4200, sol: 220, volume: 17500 },
  { name: "Dec", btc: 56000, eth: 4300, sol: 230, volume: 18000 },
];

export default function DashboardPage() {
  return (
    <div className="h-screen bg-gray-100 p-4 overflow-y-auto">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-900">
          Trading Dashboard
        </h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Trading Volume Card */}
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-300">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-700">
                Total Trading Volume
              </h3>
              <DollarSign className="h-4 w-4 text-gray-500" />
            </div>
            <div className="text-2xl font-bold mb-1 text-gray-900">$2.4M</div>
            <div className="flex items-center text-sm text-green-600">
              <ArrowUpRight className="h-4 w-4 mr-1" />
              +12.5%
            </div>
          </div>

          {/* BTC Price Card */}
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-300">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-700">BTC Price</h3>
              <Bitcoin className="h-4 w-4 text-gray-500" />
            </div>
            <div className="text-2xl font-bold mb-1 text-gray-900">
              $48,235.50
            </div>
            <div className="flex items-center text-sm text-red-600">
              <ArrowDownRight className="h-4 w-4 mr-1" />
              -2.1%
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          {/* Price Chart */}
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-300">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">
              Price Chart
            </h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={tradingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="name" stroke="#374151" />
                  <YAxis stroke="#374151" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#F3F4F6",
                      border: "1px solid #D1D5DB",
                    }}
                  />
                  <Line type="monotone" dataKey="btc" stroke="#3B82F6" />
                  <Line type="monotone" dataKey="eth" stroke="#8B5CF6" />
                  <Line type="monotone" dataKey="sol" stroke="#10B981" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Volume Chart */}
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-300">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">
              Volume Analysis
            </h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={tradingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="name" stroke="#374151" />
                  <YAxis stroke="#374151" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#F3F4F6",
                      border: "1px solid #D1D5DB",
                    }}
                  />
                  <Bar dataKey="volume" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
