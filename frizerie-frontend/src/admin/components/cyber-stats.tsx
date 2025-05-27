"use client"

import type React from "react"

import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ReactNode
  color?: string
}

export function StatCard({ title, value, change, icon, color = "#00ffff" }: StatCardProps) {
  const getTrendIcon = () => {
    if (!change) return <Minus className="w-4 h-4" />
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-400" />
    return <TrendingDown className="w-4 h-4 text-red-400" />
  }

  const getTrendColor = () => {
    if (!change) return "text-gray-400"
    return change > 0 ? "text-green-400" : "text-red-400"
  }

  return (
    <Card className="cyber-border bg-black/40 backdrop-blur-sm hover:cyber-glow transition-all duration-300 group">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm text-gray-400 uppercase tracking-wider">{title}</p>
            <p className="text-3xl font-bold" style={{ color }}>
              {typeof value === "number" ? value.toLocaleString() : value}
            </p>
            {change !== undefined && (
              <div className={cn("flex items-center space-x-1 text-sm", getTrendColor())}>
                {getTrendIcon()}
                <span>{Math.abs(change)}%</span>
              </div>
            )}
          </div>
          <div
            className="p-3 rounded-lg bg-opacity-20 group-hover:animate-glow-pulse"
            style={{ backgroundColor: color + "20", color }}
          >
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface CyberStatsProps {
  stats: Array<{
    title: string
    value: string | number
    change?: number
    icon: React.ReactNode
    color?: string
  }>
}

export function CyberStats({ stats }: CyberStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <div key={stat.title} className="animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
          <StatCard {...stat} />
        </div>
      ))}
    </div>
  )
}
