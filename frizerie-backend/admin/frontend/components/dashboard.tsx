"use client"

import React, { useState } from "react"
import { AnimatedBackground } from "./animated-background"
import { CyberSidebar } from "./cyber-sidebar"
import { CyberStats } from "./cyber-stats"
import { CyberChart } from "./cyber-chart"

const stats = [
  {
    title: "Total Revenue",
    value: "$12,345",
    change: 12.5,
    icon: "💰",
    color: "#00ff9d"
  },
  {
    title: "Appointments",
    value: "156",
    change: 8.2,
    icon: "📅",
    color: "#ff00ff"
  },
  {
    title: "New Clients",
    value: "23",
    change: -2.4,
    icon: "👥",
    color: "#00ffff"
  },
  {
    title: "Satisfaction",
    value: "4.8",
    change: 0.5,
    icon: "⭐",
    color: "#ffff00"
  },
]

const revenueData = [
  { time: "Mon", value: 1200 },
  { time: "Tue", value: 1800 },
  { time: "Wed", value: 1500 },
  { time: "Thu", value: 2100 },
  { time: "Fri", value: 2400 },
  { time: "Sat", value: 2800 },
  { time: "Sun", value: 2200 },
]

const appointmentsData = [
  { time: "9AM", value: 5 },
  { time: "10AM", value: 8 },
  { time: "11AM", value: 12 },
  { time: "12PM", value: 6 },
  { time: "1PM", value: 9 },
  { time: "2PM", value: 15 },
  { time: "3PM", value: 11 },
]

export function AdminDashboard() {
  const [activeSection, setActiveSection] = useState("dashboard")

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AnimatedBackground />
      
      <div className="relative z-10 flex">
        <CyberSidebar activeSection={activeSection} onSectionChange={setActiveSection} />
        
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-4xl font-bold cyber-text mb-8">Salon Dashboard</h1>
            
            <CyberStats stats={stats} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
              <CyberChart
                title="Revenue Overview"
                data={revenueData}
                color="#00ff9d"
              />
              <CyberChart
                title="Appointments Today"
                data={appointmentsData}
                color="#ff00ff"
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
} 