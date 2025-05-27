"use client"

import { useState } from "react"
import { Users, Plus, Edit, Trash2, Star, Calendar, Clock, AlertCircle } from "lucide-react"

interface StylistReview {
  id: number
  rating: number
  review_text: string
  created_at: string
}

interface StylistAvailability {
  id: string
  day_of_week: number
  start_time: string
  end_time: string
  is_available: boolean
  break_start?: string
  break_end?: string
}

interface StylistTimeOff {
  id: string
  start_date: string
  end_date: string
  reason: string
  is_approved: boolean
}

interface Stylist {
  id: number
  name: string
  specialization: string
  bio: string
  avatar_url: string
  is_active: boolean
  average_rating: number
  reviews: StylistReview[]
  availability: StylistAvailability[]
  time_off: StylistTimeOff[]
}

export function StaffManagement() {
  const [stylists] = useState<Stylist[]>([
    {
      id: 1,
      name: "John Smith",
      specialization: "Men's Haircuts & Styling",
      bio: "Specialized in modern men's cuts and beard grooming",
      avatar_url: "/avatars/john.jpg",
      is_active: true,
      average_rating: 4.8,
      reviews: [
        {
          id: 1,
          rating: 5.0,
          review_text: "Excellent service!",
          created_at: "2024-03-15T10:00:00Z"
        }
      ],
      availability: [
        {
          id: "1",
          day_of_week: 1,
          start_time: "09:00",
          end_time: "17:00",
          is_available: true,
          break_start: "12:00",
          break_end: "13:00"
        }
      ],
      time_off: []
    }
  ])

  return (
    <div className="cyber-card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold cyber-text">Staff Management</h2>
        <button className="cyber-button">
          <Plus className="w-4 h-4 mr-2" />
          Add Staff
        </button>
      </div>

      <div className="space-y-4">
        {stylists.map((stylist) => (
          <div key={stylist.id} className="cyber-card bg-gray-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center overflow-hidden">
                  {stylist.avatar_url ? (
                    <img src={stylist.avatar_url} alt={stylist.name} className="w-full h-full object-cover" />
                  ) : (
                    <Users className="w-6 h-6 text-cyan-400" />
                  )}
                </div>
                <div>
                  <h3 className="font-medium">{stylist.name}</h3>
                  <p className="text-sm text-gray-400">{stylist.specialization}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-400 mr-1" />
                  <span>{stylist.average_rating}</span>
                </div>
                <div className="flex items-center text-sm">
                  <Calendar className="w-4 h-4 text-blue-400 mr-1" />
                  <span>{stylist.availability.length} schedules</span>
                </div>
                <div className="flex items-center text-sm">
                  <Clock className="w-4 h-4 text-purple-400 mr-1" />
                  <span>{stylist.time_off.length} time off</span>
                </div>
                <div className={`px-2 py-1 rounded text-xs ${
                  stylist.is_active ? "bg-green-400/20 text-green-400" : "bg-red-400/20 text-red-400"
                }`}>
                  {stylist.is_active ? "Active" : "Inactive"}
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
            
            {/* Additional Details */}
            <div className="mt-4 pt-4 border-t border-gray-800">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Bio</h4>
                  <p className="text-sm text-gray-400">{stylist.bio}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">Recent Reviews</h4>
                  <div className="space-y-2">
                    {stylist.reviews.slice(0, 2).map((review) => (
                      <div key={review.id} className="text-sm">
                        <div className="flex items-center">
                          <Star className="w-3 h-3 text-yellow-400 mr-1" />
                          <span>{review.rating}</span>
                        </div>
                        <p className="text-gray-400">{review.review_text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 