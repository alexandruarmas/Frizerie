import React from 'react';
import { LoyaltyStatus } from '../services/users';

interface LoyaltyCardProps {
  loyaltyStatus: LoyaltyStatus;
  isLoading?: boolean;
}

const LoyaltyCard: React.FC<LoyaltyCardProps> = ({ loyaltyStatus, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-24 bg-gray-200 rounded mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  // Determine background color based on tier
  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'DIAMOND':
        return 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white';
      case 'GOLD':
        return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white';
      case 'SILVER':
        return 'bg-gradient-to-r from-gray-400 to-gray-600 text-white';
      case 'BRONZE':
      default:
        return 'bg-gradient-to-r from-amber-500 to-amber-700 text-white';
    }
  };

  // Calculate percentage to next tier
  const calculateProgress = () => {
    if (!loyaltyStatus.next_tier) return 100;
    
    const pointsNeeded = loyaltyStatus.next_tier.points_needed;
    const currentPoints = loyaltyStatus.points;
    const previousTierPoints = currentPoints - pointsNeeded;
    
    return Math.min(100, Math.max(0, (currentPoints / (previousTierPoints + pointsNeeded)) * 100));
  };

  const progressPercentage = calculateProgress();

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className={`p-6 ${getTierColor(loyaltyStatus.tier)}`}>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-semibold">Loyalty Status</h3>
          <span className="text-xs font-medium px-2 py-1 bg-white bg-opacity-20 rounded-full">
            {loyaltyStatus.tier}
          </span>
        </div>
        
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold">{loyaltyStatus.points}</span>
          </div>
          <div>
            <p className="text-sm font-medium">Current Points</p>
            <p className="text-xs opacity-80">{loyaltyStatus.bookings_count} bookings completed</p>
          </div>
        </div>
        
        {loyaltyStatus.next_tier && (
          <div className="mb-2">
            <div className="flex justify-between text-xs mb-1">
              <span>Progress to {loyaltyStatus.next_tier.name}</span>
              <span>{loyaltyStatus.next_tier.points_needed} points needed</span>
            </div>
            <div className="h-2 bg-white bg-opacity-20 rounded-full">
              <div 
                className="h-2 bg-white rounded-full" 
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Your Benefits</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          {loyaltyStatus.perks.map((perk, index) => (
            <li key={index} className="flex items-start">
              <span className="text-primary-500 mr-2">✓</span>
              {perk}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default LoyaltyCard; 