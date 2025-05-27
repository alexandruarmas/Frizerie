"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface DataPoint {
  time: string
  value: number
}

interface CyberChartProps {
  title: string
  data: DataPoint[]
  color?: string
  height?: number
}

export function CyberChart({ title, data, color = "#00ffff", height = 200 }: CyberChartProps) {
  const [animatedData, setAnimatedData] = useState<DataPoint[]>([])

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data)
    }, 300)
    return () => clearTimeout(timer)
  }, [data])

  const maxValue = Math.max(...data.map((d) => d.value))
  const minValue = Math.min(...data.map((d) => d.value))
  const range = maxValue - minValue

  const getY = (value: number) => {
    return height - ((value - minValue) / range) * (height - 40)
  }

  const pathData = animatedData
    .map((point, index) => {
      const x = (index / (animatedData.length - 1)) * 300
      const y = getY(point.value)
      return `${index === 0 ? "M" : "L"} ${x} ${y}`
    })
    .join(" ")

  return (
    <Card className="cyber-border bg-black/40 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="cyber-text text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative" style={{ height }}>
          <svg width="100%" height="100%" viewBox={`0 0 300 ${height}`} className="overflow-visible">
            {/* Grid lines */}
            <defs>
              <pattern id="grid" width="30" height="20" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 20" fill="none" stroke={color} strokeWidth="0.5" opacity="0.2" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Gradient fill */}
            <defs>
              <linearGradient id={`gradient-${title}`} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                <stop offset="100%" stopColor={color} stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Area fill */}
            {animatedData.length > 0 && (
              <path
                d={`${pathData} L 300 ${height} L 0 ${height} Z`}
                fill={`url(#gradient-${title})`}
                className="animate-fade-in"
              />
            )}

            {/* Line */}
            {animatedData.length > 0 && (
              <path
                d={pathData}
                fill="none"
                stroke={color}
                strokeWidth="2"
                className="animate-fade-in"
                style={{
                  filter: `drop-shadow(0 0 4px ${color})`,
                }}
              />
            )}

            {/* Data points */}
            {animatedData.map((point, index) => {
              const x = (index / (animatedData.length - 1)) * 300
              const y = getY(point.value)
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="3"
                  fill={color}
                  className="animate-glow-pulse"
                  style={{
                    filter: `drop-shadow(0 0 6px ${color})`,
                    animationDelay: `${index * 0.1}s`,
                  }}
                />
              )
            })}
          </svg>

          {/* Value labels */}
          <div className="absolute top-2 right-2 text-right">
            <div className="text-2xl font-bold" style={{ color }}>
              {data[data.length - 1]?.value.toLocaleString()}
            </div>
            <div className="text-xs text-gray-400">Current</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
