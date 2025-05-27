"use client"

import { useState } from "react"
import { Calendar, Plus, Edit, Trash2, User, Clock, Check, X, AlertCircle, Repeat } from "lucide-react"

interface Booking {
  id: string
  user_id: number
  stylist_id: number
  service_id: number
  start_time: string
  end_time: string
  status: "pending" | "confirmed" | "cancelled" | "completed" | "no_show" | "waitlisted"
  notes: string
  recurrence_type: "none" | "daily" | "weekly" | "biweekly" | "monthly" | "custom"
  recurrence_end_date?: string
  recurrence_pattern?: any
  parent_booking_id?: string
  calendar_event_id?: string
  reminder_sent: boolean
  cancellation_reason?: string
  cancellation_time?: string
  no_show_count: number
  last_modified_by?: number
  user: {
    name: string
  }
  stylist: {
    name: string
  }
  service: {
    name: string
  }
}

export function BookingManagement() {
  const [bookings] = useState<Booking[]>([
    {
      id: "1",
      user_id: 1,
      stylist_id: 1,
      service_id: 1,
      start_time: "2024-03-20T14:00:00Z",
      end_time: "2024-03-20T14:30:00Z",
      status: "confirmed",
      notes: "Regular haircut",
      recurrence_type: "none",
      reminder_sent: true,
      no_show_count: 0,
      user: {
        name: "Alice Johnson"
      },
      stylist: {
        name: "John Smith"
      },
      service: {
        name: "Men's Haircut"
      }
    },
    {
      id: "2",
      user_id: 2,
      stylist_id: 2,
      service_id: 2,
      start_time: "2024-03-20T15:30:00Z",
      end_time: "2024-03-20T16:30:00Z",
      status: "pending",
      notes: "First time visit",
      recurrence_type: "none",
      reminder_sent: false,
      no_show_count: 0,
      user: {
        name: "Bob Smith"
      },
      stylist: {
        name: "Sarah Johnson"
      },
      service: {
        name: "Women's Haircut"
      }
    },
    {
      id: "3",
      user_id: 3,
      stylist_id: 3,
      service_id: 3,
      start_time: "2024-03-20T16:00:00Z",
      end_time: "2024-03-20T18:00:00Z",
      status: "cancelled",
      notes: "Client requested cancellation",
      recurrence_type: "none",
      reminder_sent: true,
      no_show_count: 0,
      cancellation_reason: "Client unavailable",
      cancellation_time: "2024-03-19T10:00:00Z",
      user: {
        name: "Carol White"
      },
      stylist: {
        name: "Mike Brown"
      },
      service: {
        name: "Full Color"
      }
    }
  ])

  return (
    <div className="cyber-card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold cyber-text">Booking Management</h2>
        <button className="cyber-button">
          <Plus className="w-4 h-4 mr-2" />
          New Booking
        </button>
      </div>

      <div className="space-y-4">
        {bookings.map((booking) => (
          <div key={booking.id} className="cyber-card bg-gray-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="font-medium">{booking.user.name}</h3>
                  <p className="text-sm text-gray-400">{booking.service.name}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm">
                  <User className="w-4 h-4 text-blue-400 mr-1" />
                  <span>{booking.stylist.name}</span>
                </div>
                <div className="flex items-center text-sm">
                  <Clock className="w-4 h-4 text-yellow-400 mr-1" />
                  <span>{new Date(booking.start_time).toLocaleTimeString()}</span>
                </div>
                {booking.recurrence_type !== "none" && (
                  <div className="flex items-center text-sm">
                    <Repeat className="w-4 h-4 text-green-400 mr-1" />
                    <span>{booking.recurrence_type}</span>
                  </div>
                )}
                {booking.no_show_count > 0 && (
                  <div className="flex items-center text-sm">
                    <AlertCircle className="w-4 h-4 text-red-400 mr-1" />
                    <span>{booking.no_show_count} no-shows</span>
                  </div>
                )}
                <div className={`px-2 py-1 rounded text-xs ${
                  booking.status === "confirmed" ? "bg-green-400/20 text-green-400" :
                  booking.status === "pending" ? "bg-yellow-400/20 text-yellow-400" :
                  booking.status === "cancelled" ? "bg-red-400/20 text-red-400" :
                  booking.status === "completed" ? "bg-blue-400/20 text-blue-400" :
                  booking.status === "no_show" ? "bg-red-400/20 text-red-400" :
                  "bg-purple-400/20 text-purple-400"
                }`}>
                  {booking.status}
                </div>
                <div className="flex space-x-2">
                  {booking.status === "pending" && (
                    <button className="cyber-button-small text-green-400">
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                  <button className="cyber-button-small">
                    <Edit className="w-4 h-4" />
                  </button>
                  {booking.status !== "cancelled" && (
                    <button className="cyber-button-small text-red-400">
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            {/* Additional Details */}
            {(booking.notes || booking.cancellation_reason) && (
              <div className="mt-4 pt-4 border-t border-gray-800">
                <div className="grid grid-cols-2 gap-4">
                  {booking.notes && (
                    <div>
                      <h4 className="text-sm font-medium mb-2">Notes</h4>
                      <p className="text-sm text-gray-400">{booking.notes}</p>
                    </div>
                  )}
                  {booking.cancellation_reason && (
                    <div>
                      <h4 className="text-sm font-medium mb-2">Cancellation Reason</h4>
                      <p className="text-sm text-gray-400">{booking.cancellation_reason}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
} 