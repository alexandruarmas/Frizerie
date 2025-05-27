"use client"

import { useState } from "react"
import {
  BarChart3,
  Users,
  Shield,
  Activity,
  Settings,
  Database,
  Zap,
  ChevronLeft,
  ChevronRight,
  Home,
  Bell,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const menuItems = [
  { icon: Home, label: "Dashboard", id: "dashboard", active: true },
  { icon: BarChart3, label: "Analytics", id: "analytics" },
  { icon: Users, label: "Users", id: "users" },
  { icon: Shield, label: "Security", id: "security" },
  { icon: Activity, label: "Monitoring", id: "monitoring" },
  { icon: Database, label: "Database", id: "database" },
  { icon: Bell, label: "Alerts", id: "alerts" },
  { icon: Settings, label: "Settings", id: "settings" },
]

interface CyberSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

export function CyberSidebar({ activeSection, onSectionChange }: CyberSidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div
      className={cn(
        "relative h-screen bg-black/40 backdrop-blur-sm border-r border-cyan-400/30 transition-all duration-300 cyber-glow",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-cyan-400/30">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center space-x-2 animate-slide-in">
              <Zap className="w-8 h-8 text-cyan-400 animate-glow-pulse" />
              <span className="text-xl font-bold cyber-text">NEXUS</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="neon-button text-cyan-400 hover:text-cyan-300"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item, index) => {
          const Icon = item.icon
          const isActive = activeSection === item.id

          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={cn(
                "w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 group relative overflow-hidden",
                isActive
                  ? "bg-cyan-400/20 text-cyan-400 cyber-glow"
                  : "text-gray-400 hover:text-cyan-400 hover:bg-cyan-400/10",
                collapsed && "justify-center",
              )}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 to-purple-400/20 animate-fade-in" />
              )}
              <Icon className={cn("w-5 h-5 relative z-10", isActive && "animate-glow-pulse")} />
              {!collapsed && <span className="relative z-10 font-medium animate-slide-in">{item.label}</span>}
              {isActive && !collapsed && (
                <div className="absolute right-2 w-2 h-2 bg-cyan-400 rounded-full animate-glow-pulse" />
              )}
            </button>
          )
        })}
      </nav>

      {/* Status indicator */}
      <div className="absolute bottom-4 left-4 right-4">
        <div
          className={cn(
            "flex items-center space-x-2 p-2 rounded-lg bg-green-400/20 border border-green-400/30",
            collapsed && "justify-center",
          )}
        >
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          {!collapsed && <span className="text-xs text-green-400 font-medium">SYSTEM ONLINE</span>}
        </div>
      </div>
    </div>
  )
}
