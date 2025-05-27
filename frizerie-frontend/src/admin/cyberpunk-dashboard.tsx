"use client"

import { useState, useEffect } from "react"
import { AnimatedBackground } from "./components/animated-background"
import { CyberSidebar } from "./components/cyber-sidebar"
import { CyberStats } from "./components/cyber-stats"
import { CyberChart } from "./components/cyber-chart"
import { StaffManagement } from "./components/staff-management"
import { ServiceManagement } from "./components/service-management"
import { BookingManagement } from "./components/booking-management"
import { 
  Users, 
  Calendar, 
  Scissors, 
  DollarSign, 
  Star,
  BarChart,
  Settings,
  Bell
} from "lucide-react"

// Mock data for charts
const generateChartData = (points: number) => {
  return Array.from({ length: points }, (_, i) => ({
    time: `${i}:00`,
    value: Math.floor(Math.random() * 100) + 20,
  }))
}

export default function SalonDashboard() {
  const [activeSection, setActiveSection] = useState("dashboard")
  const [stats, setStats] = useState([
    {
      title: "Today's Appointments",
      value: 24,
      change: 5,
      icon: <Calendar className="w-6 h-6" />,
      color: "#00ffff",
    },
    {
      title: "Active Stylists",
      value: 8,
      change: 0,
      icon: <Users className="w-6 h-6" />,
      color: "#ff00ff",
    },
    {
      title: "Revenue Today",
      value: "$1,284",
      change: 12,
      icon: <DollarSign className="w-6 h-6" />,
      color: "#00ff00",
    },
    {
      title: "Customer Satisfaction",
      value: "98.5%",
      change: 2,
      icon: <Star className="w-6 h-6" />,
      color: "#ffff00",
    },
  ])

  const [chartData] = useState({
    appointments: generateChartData(24),
    revenue: generateChartData(24),
    customers: generateChartData(24),
    services: generateChartData(24),
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) =>
        prev.map((stat) => ({
          ...stat,
          change: Math.floor(Math.random() * 20) - 10,
        })),
      )
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const renderContent = () => {
    switch (activeSection) {
      case "staff":
        return <StaffManagement />
      case "services":
        return <ServiceManagement />
      case "bookings":
        return <BookingManagement />
      case "analytics":
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CyberChart title="Appointment Trends" data={chartData.appointments} color="#00ffff" />
              <CyberChart title="Revenue Analysis" data={chartData.revenue} color="#ff00ff" />
              <CyberChart title="Customer Growth" data={chartData.customers} color="#00ff00" />
              <CyberChart title="Service Popularity" data={chartData.services} color="#ffff00" />
            </div>
          </div>
        )
      default:
        return (
          <div className="space-y-6">
            <CyberStats stats={stats} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CyberChart title="Today's Appointments" data={chartData.appointments} color="#00ffff" />
              <CyberChart title="Revenue Overview" data={chartData.revenue} color="#ff00ff" />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <StaffManagement />
              <div className="lg:col-span-2">
                <BookingManagement />
              </div>
            </div>
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AnimatedBackground />

      <div className="flex relative z-10">
        <CyberSidebar activeSection={activeSection} onSectionChange={setActiveSection} />

        <main className="flex-1 p-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-bold cyber-text mb-2">SALON CONTROL CENTER</h1>
                  <p className="text-gray-400">Advanced salon management interface</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-green-400/20 border border-green-400/30">
                    <Bell className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm font-medium">3 NEW APPOINTMENTS</span>
                  </div>
                  <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-400/20 border border-blue-400/30">
                    <Settings className="w-4 h-4 text-blue-400" />
                    <span className="text-blue-400 text-sm font-medium">SYSTEM STATUS</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="animate-fade-in">{renderContent()}</div>
          </div>
        </main>
      </div>
    </div>
  )
}
