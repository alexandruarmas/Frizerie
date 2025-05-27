"use client"

import React from "react"
import { 
  BarChart, 
  Users, 
  Scissors, 
  Calendar, 
  DollarSign,
  Settings,
  LogOut
} from "lucide-react"

interface CyberSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

export function CyberSidebar({ activeSection, onSectionChange }: CyberSidebarProps) {
  const menuItems = [
    { id: "dashboard", icon: <BarChart className="w-5 h-5" />, label: "Dashboard" },
    { id: "staff", icon: <Users className="w-5 h-5" />, label: "Staff" },
    { id: "services", icon: <Scissors className="w-5 h-5" />, label: "Services" },
    { id: "bookings", icon: <Calendar className="w-5 h-5" />, label: "Bookings" },
    { id: "analytics", icon: <DollarSign className="w-5 h-5" />, label: "Analytics" },
  ]

  return (
    <div className="w-64 min-h-screen bg-black/40 backdrop-blur-sm border-r border-cyan-400/20 p-4">
      <div className="mb-8">
        <h1 className="text-2xl font-bold cyber-text">SALON ADMIN</h1>
        <p className="text-sm text-gray-400">Control Center</p>
      </div>

      <nav className="space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onSectionChange(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              activeSection === item.id
                ? "bg-cyan-400/20 text-cyan-400 border border-cyan-400/30"
                : "text-gray-400 hover:text-cyan-400 hover:bg-cyan-400/10"
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-400/10 transition-all duration-200">
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  )
} 