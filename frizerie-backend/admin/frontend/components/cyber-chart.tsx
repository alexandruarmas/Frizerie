"use client"

import React from "react"

interface ChartData {
  time: string
  value: number
}

interface CyberChartProps {
  title: string
  data: ChartData[]
  color: string
}

export function CyberChart({ title, data, color }: CyberChartProps) {
  const maxValue = Math.max(...data.map((d) => d.value))
  const minValue = Math.min(...data.map((d) => d.value))
  const range = maxValue - minValue

  return (
    <div className="cyber-card">
      <h3 className="text-xl font-bold cyber-text mb-4">{title}</h3>
      <div className="relative h-48">
        {/* Grid lines */}
        <div className="absolute inset-0 grid grid-rows-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="border-t border-cyan-400/10"
              style={{ top: `${(i * 100) / 3}%` }}
            />
          ))}
        </div>

        {/* Chart bars */}
        <div className="absolute inset-0 flex items-end space-x-1">
          {data.map((point, index) => {
            const height = ((point.value - minValue) / range) * 100
            return (
              <div
                key={index}
                className="flex-1 bg-gradient-to-t"
                style={{
                  height: `${height}%`,
                  background: `linear-gradient(to top, ${color}40, ${color}80)`,
                  boxShadow: `0 0 10px ${color}40`,
                }}
              />
            )
          })}
        </div>

        {/* Time labels */}
        <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-gray-400">
          {data.map((point, index) => (
            <span key={index}>{point.time}</span>
          ))}
        </div>
      </div>
    </div>
  )
} 