import React, { useState } from 'react';
import { LoyaltyStatus, LoyaltyReward, LoyaltyRedemption, LoyaltyPointsHistory } from '../services/users';
import { format } from 'date-fns';

interface LoyaltyCardProps {
  loyaltyStatus: LoyaltyStatus;
  isLoading?: boolean;
  onRedeemReward?: (rewardId: number) => void;
}

const LoyaltyCard: React.FC<LoyaltyCardProps> = ({ 
  loyaltyStatus, 
  isLoading = false,
  onRedeemReward 
}) => {
  const [activeTab, setActiveTab] = useState<'status' | 'rewards' | 'history'>('status');

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

  const renderStatusTab = () => (
    <>
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
      
      <div className="p-6">
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
    </>
  );

  const renderRewardsTab = () => (
    <div className="p-6">
      <h4 className="text-sm font-medium text-gray-700 mb-4">Available Rewards</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loyaltyStatus.available_rewards.map((reward) => (
          <div key={reward.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex justify-between items-start mb-2">
              <h5 className="font-medium text-gray-900">{reward.name}</h5>
              <span className="text-sm font-medium text-primary-600">
                {reward.points_cost} points
              </span>
            </div>
            {reward.description && (
              <p className="text-sm text-gray-600 mb-3">{reward.description}</p>
            )}
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>{reward.reward_type}</span>
              {reward.min_tier_required && (
                <span className="px-2 py-1 bg-gray-200 rounded-full">
                  {reward.min_tier_required} tier
                </span>
              )}
            </div>
            {onRedeemReward && (
              <button
                onClick={() => onRedeemReward(reward.id)}
                className="mt-3 w-full bg-primary-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-primary-700 transition-colors"
              >
                Redeem
              </button>
            )}
          </div>
        ))}
      </div>

      {loyaltyStatus.recent_redemptions.length > 0 && (
        <div className="mt-8">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Recent Redemptions</h4>
          <div className="space-y-3">
            {loyaltyStatus.recent_redemptions.map((redemption) => (
              <div key={redemption.id} className="flex justify-between items-center text-sm">
                <div>
                  <p className="font-medium text-gray-900">
                    {redemption.reward?.name || 'Unknown Reward'}
                  </p>
                  <p className="text-gray-500">
                    {format(new Date(redemption.redeemed_at), 'MMM d, yyyy')}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  redemption.status === 'COMPLETED' 
                    ? 'bg-green-100 text-green-800'
                    : redemption.status === 'PENDING'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {redemption.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderHistoryTab = () => (
    <div className="p-6">
      <h4 className="text-sm font-medium text-gray-700 mb-4">Points History</h4>
      <div className="space-y-3">
        {loyaltyStatus.points_history.map((entry) => (
          <div key={entry.id} className="flex justify-between items-center text-sm">
            <div>
              <p className="font-medium text-gray-900">
                {entry.reason.replace(/_/g, ' ').toLowerCase()}
              </p>
              <p className="text-gray-500">
                {format(new Date(entry.created_at), 'MMM d, yyyy')}
              </p>
            </div>
            <span className={`font-medium ${
              entry.points_change > 0 
                ? 'text-green-600'
                : 'text-red-600'
            }`}>
              {entry.points_change > 0 ? '+' : ''}{entry.points_change}
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="border-b border-gray-200">
        <nav className="flex">
          <button
            onClick={() => setActiveTab('status')}
            className={`flex-1 py-3 px-4 text-center text-sm font-medium ${
              activeTab === 'status'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Status
          </button>
          <button
            onClick={() => setActiveTab('rewards')}
            className={`flex-1 py-3 px-4 text-center text-sm font-medium ${
              activeTab === 'rewards'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Rewards
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 py-3 px-4 text-center text-sm font-medium ${
              activeTab === 'history'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            History
          </button>
        </nav>
      </div>

      {activeTab === 'status' && renderStatusTab()}
      {activeTab === 'rewards' && renderRewardsTab()}
      {activeTab === 'history' && renderHistoryTab()}
    </div>
  );
};

export default LoyaltyCard; 