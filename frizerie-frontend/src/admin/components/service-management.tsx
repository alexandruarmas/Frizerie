"use client"

import { useState } from "react"
import { Scissors, Plus, Edit, Trash2, Clock, DollarSign, Tag } from "lucide-react"

interface ServiceCategory {
  id: number
  name: string
  description: string
}

interface Service {
  id: number
  name: string
  description: string
  price: number
  duration_minutes: number
  category_id: number
  is_active: boolean
  category?: ServiceCategory
}

export function ServiceManagement() {
  const [services] = useState<Service[]>([
    {
      id: 1,
      name: "Men's Haircut",
      description: "Classic men's haircut with clippers and scissors",
      price: 25,
      duration_minutes: 30,
      category_id: 1,
      is_active: true,
      category: {
        id: 1,
        name: "Haircuts",
        description: "Basic haircut services"
      }
    },
    {
      id: 2,
      name: "Women's Haircut",
      description: "Women's haircut with styling",
      price: 45,
      duration_minutes: 60,
      category_id: 1,
      is_active: true,
      category: {
        id: 1,
        name: "Haircuts",
        description: "Basic haircut services"
      }
    },
    {
      id: 3,
      name: "Full Color",
      description: "Complete hair coloring service",
      price: 85,
      duration_minutes: 120,
      category_id: 2,
      is_active: true,
      category: {
        id: 2,
        name: "Coloring",
        description: "Hair coloring services"
      }
    }
  ])

  return (
    <div className="cyber-card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold cyber-text">Service Management</h2>
        <button className="cyber-button">
          <Plus className="w-4 h-4 mr-2" />
          Add Service
        </button>
      </div>

      <div className="space-y-4">
        {services.map((service) => (
          <div key={service.id} className="cyber-card bg-gray-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center">
                  <Scissors className="w-6 h-6 text-pink-400" />
                </div>
                <div>
                  <h3 className="font-medium">{service.name}</h3>
                  <p className="text-sm text-gray-400">{service.description}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm">
                  <Tag className="w-4 h-4 text-blue-400 mr-1" />
                  <span>{service.category?.name}</span>
                </div>
                <div className="flex items-center text-sm">
                  <Clock className="w-4 h-4 text-yellow-400 mr-1" />
                  <span>{service.duration_minutes} min</span>
                </div>
                <div className="flex items-center text-sm">
                  <DollarSign className="w-4 h-4 text-green-400 mr-1" />
                  <span>${service.price}</span>
                </div>
                <div className={`px-2 py-1 rounded text-xs ${
                  service.is_active ? "bg-green-400/20 text-green-400" : "bg-red-400/20 text-red-400"
                }`}>
                  {service.is_active ? "Active" : "Inactive"}
                </div>
                <div className="flex space-x-2">
                  <button className="cyber-button-small">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="cyber-button-small text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 