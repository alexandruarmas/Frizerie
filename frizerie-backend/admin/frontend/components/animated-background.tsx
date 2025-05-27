"use client"

import React, { useEffect, useState } from "react"

interface Particle {
  x: number
  y: number
  size: number
  speedX: number
  speedY: number
  opacity: number
  delay: number
}

export function AnimatedBackground() {
  const [particles, setParticles] = useState<Particle[]>([])

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      size: Math.random() * 2 + 1,
      speedX: (Math.random() - 0.5) * 0.5,
      speedY: (Math.random() - 0.5) * 0.5,
      opacity: Math.random() * 0.5 + 0.1,
      delay: Math.random() * 2,
    }))
    setParticles(newParticles)
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none">
      {/* Floating particles */}
      {particles.map((particle, index) => (
        <div
          key={index}
          className="absolute rounded-full bg-cyan-400"
          style={{
            left: `${particle.x}px`,
            top: `${particle.y}px`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            opacity: particle.opacity,
            animation: `float ${particle.delay}s infinite`,
          }}
        />
      ))}

      {/* Scanning lines */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/5 to-transparent animate-scan" />
      </div>

      {/* Corner decorations */}
      <div className="absolute top-0 left-0 w-32 h-32 border-t-2 border-l-2 border-cyan-400/20" />
      <div className="absolute top-0 right-0 w-32 h-32 border-t-2 border-r-2 border-cyan-400/20" />
      <div className="absolute bottom-0 left-0 w-32 h-32 border-b-2 border-l-2 border-cyan-400/20" />
      <div className="absolute bottom-0 right-0 w-32 h-32 border-b-2 border-r-2 border-cyan-400/20" />
    </div>
  )
} 