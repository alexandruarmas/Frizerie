"use client"

import React from "react"

interface Stat {
  title: string
  value: string
  change: number
  icon: string
  color?: string
}

interface CyberStatsProps {
  stats: Stat[]
}

export function CyberStats({ stats }: CyberStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <div
          key={stat.title}
          className="cyber-card bg-black/40 backdrop-blur-sm"
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${stat.color || "#00ff9d"}20` }}>
                {stat.icon}
              </div>
              <div>
                <h3 className="text-sm text-gray-400">{stat.title}</h3>
                <p className="text-2xl font-bold" style={{ color: stat.color || "#00ff9d" }}>
                  {stat.value}
                </p>
              </div>
            </div>
            <div
              className={`text-sm font-medium ${
                stat.change >= 0 ? "text-green-400" : "text-red-400"
              }`}
            >
              {stat.change >= 0 ? "+" : ""}
              {stat.change}%
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 