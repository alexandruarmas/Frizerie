"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Cpu, HardDrive, MemoryStick, Wifi, Server, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface SystemMetric {
  name: string
  value: number
  max: number
  unit: string
  status: "good" | "warning" | "critical"
  icon: React.ReactNode
}

interface SystemAlert {
  id: string
  type: "info" | "warning" | "error"
  message: string
  timestamp: string
}

export function SystemMonitoring() {
  const [metrics, setMetrics] = useState<SystemMetric[]>([
    {
      name: "CPU Usage",
      value: 45,
      max: 100,
      unit: "%",
      status: "good",
      icon: <Cpu className="w-5 h-5" />,
    },
    {
      name: "Memory",
      value: 12.4,
      max: 16,
      unit: "GB",
      status: "warning",
      icon: <MemoryStick className="w-5 h-5" />,
    },
    {
      name: "Disk Usage",
      value: 850,
      max: 1000,
      unit: "GB",
      status: "critical",
      icon: <HardDrive className="w-5 h-5" />,
    },
    {
      name: "Network",
      value: 125,
      max: 1000,
      unit: "Mbps",
      status: "good",
      icon: <Wifi className="w-5 h-5" />,
    },
  ])

  const [alerts] = useState<SystemAlert[]>([
    {
      id: "1",
      type: "warning",
      message: "High memory usage detected on Server-02",
      timestamp: "2 min ago",
    },
    {
      id: "2",
      type: "error",
      message: "Disk space critical on Database Server",
      timestamp: "5 min ago",
    },
    {
      id: "3",
      type: "info",
      message: "Backup completed successfully",
      timestamp: "15 min ago",
    },
  ])

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) =>
        prev.map((metric) => ({
          ...metric,
          value: Math.max(0, metric.value + (Math.random() - 0.5) * 5),
        })),
      )
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good":
        return "text-green-400"
      case "warning":
        return "text-yellow-400"
      case "critical":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const getProgressColor = (status: string) => {
    switch (status) {
      case "good":
        return "bg-green-400"
      case "warning":
        return "bg-yellow-400"
      case "critical":
        return "bg-red-400"
      default:
        return "bg-gray-400"
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "info":
        return <CheckCircle className="w-4 h-4 text-blue-400" />
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case "error":
        return <XCircle className="w-4 h-4 text-red-400" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* System Metrics */}
      <Card className="cyber-border bg-black/40 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="cyber-text text-xl flex items-center">
            <Server className="w-6 h-6 mr-2" />
            System Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {metrics.map((metric, index) => (
              <div
                key={metric.name}
                className="space-y-3 animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={getStatusColor(metric.status)}>{metric.icon}</div>
                    <span className="text-cyan-100 font-medium">{metric.name}</span>
                  </div>
                  <div className="text-right">
                    <span className={`text-lg font-bold ${getStatusColor(metric.status)}`}>
                      {metric.value.toFixed(1)}
                      {metric.unit}
                    </span>
                    <div className="text-xs text-gray-400">
                      / {metric.max}
                      {metric.unit}
                    </div>
                  </div>
                </div>
                <div className="relative">
                  <Progress value={(metric.value / metric.max) * 100} className="h-2 bg-gray-700" />
                  <div
                    className={`absolute top-0 left-0 h-2 rounded-full transition-all duration-500 ${getProgressColor(metric.status)}`}
                    style={{
                      width: `${(metric.value / metric.max) * 100}%`,
                      boxShadow: `0 0 10px ${metric.status === "good" ? "#00ff00" : metric.status === "warning" ? "#ffff00" : "#ff0000"}`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Alerts */}
      <Card className="cyber-border bg-black/40 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="cyber-text text-xl">System Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div
                key={alert.id}
                className="flex items-start space-x-3 p-3 rounded-lg bg-black/20 border border-cyan-400/20 animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <p className="text-cyan-100 text-sm">{alert.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{alert.timestamp}</p>
                </div>
                <Badge
                  className={`
                    ${alert.type === "info" ? "bg-blue-400/20 text-blue-400 border-blue-400/30" : ""}
                    ${alert.type === "warning" ? "bg-yellow-400/20 text-yellow-400 border-yellow-400/30" : ""}
                    ${alert.type === "error" ? "bg-red-400/20 text-red-400 border-red-400/30" : ""}
                    border
                  `}
                >
                  {alert.type.toUpperCase()}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
