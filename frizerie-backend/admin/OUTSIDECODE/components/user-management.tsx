"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, UserPlus, MoreVertical, Shield, ShieldCheck, ShieldX, Eye, Edit, Trash2 } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface User {
  id: string
  name: string
  email: string
  role: "admin" | "user" | "moderator"
  status: "active" | "inactive" | "suspended"
  lastActive: string
  avatar?: string
}

const mockUsers: User[] = [
  {
    id: "1",
    name: "Alex Chen",
    email: "alex.chen@nexus.corp",
    role: "admin",
    status: "active",
    lastActive: "2 min ago",
  },
  {
    id: "2",
    name: "Sarah Connor",
    email: "s.connor@nexus.corp",
    role: "moderator",
    status: "active",
    lastActive: "15 min ago",
  },
  {
    id: "3",
    name: "Marcus Johnson",
    email: "m.johnson@nexus.corp",
    role: "user",
    status: "inactive",
    lastActive: "2 hours ago",
  },
  {
    id: "4",
    name: "Elena Vasquez",
    email: "e.vasquez@nexus.corp",
    role: "user",
    status: "suspended",
    lastActive: "1 day ago",
  },
  {
    id: "5",
    name: "David Kim",
    email: "d.kim@nexus.corp",
    role: "moderator",
    status: "active",
    lastActive: "5 min ago",
  },
]

export function UserManagement() {
  const [users] = useState<User[]>(mockUsers)
  const [searchTerm, setSearchTerm] = useState("")

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "admin":
        return <ShieldCheck className="w-4 h-4 text-red-400" />
      case "moderator":
        return <Shield className="w-4 h-4 text-yellow-400" />
      default:
        return <ShieldX className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      active: "bg-green-400/20 text-green-400 border-green-400/30",
      inactive: "bg-gray-400/20 text-gray-400 border-gray-400/30",
      suspended: "bg-red-400/20 text-red-400 border-red-400/30",
    }

    return <Badge className={`${variants[status as keyof typeof variants]} border`}>{status.toUpperCase()}</Badge>
  }

  return (
    <Card className="cyber-border bg-black/40 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="cyber-text text-xl">User Management</CardTitle>
          <Button className="neon-button text-cyan-400 hover:text-cyan-300">
            <UserPlus className="w-4 h-4 mr-2" />
            Add User
          </Button>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-black/20 border-cyan-400/30 text-cyan-100 placeholder-gray-400"
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {filteredUsers.map((user, index) => (
            <div
              key={user.id}
              className="flex items-center justify-between p-4 rounded-lg bg-black/20 border border-cyan-400/20 hover:border-cyan-400/40 transition-all duration-200 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-purple-400 flex items-center justify-center text-black font-bold">
                  {user.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-medium text-cyan-100">{user.name}</h3>
                    {getRoleIcon(user.role)}
                  </div>
                  <p className="text-sm text-gray-400">{user.email}</p>
                  <p className="text-xs text-gray-500">Last active: {user.lastActive}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {getStatusBadge(user.status)}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="text-gray-400 hover:text-cyan-400">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-black/90 border-cyan-400/30">
                    <DropdownMenuItem className="text-cyan-100 hover:text-cyan-400">
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-cyan-100 hover:text-cyan-400">
                      <Edit className="w-4 h-4 mr-2" />
                      Edit User
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-red-400 hover:text-red-300">
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete User
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
