import React from 'react';
import { Shield } from 'lucide-react';

interface ToolHealthBadgeProps {
  score?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const getGrade = (score: number): string => {
  if (score >= 90) return 'A+';
  if (score >= 80) return 'A';
  if (score >= 70) return 'B';
  if (score >= 60) return 'C';
  if (score >= 50) return 'D';
  return 'F';
};

const getColor = (score: number): { bg: string; text: string; border: string } => {
  if (score >= 80) return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' };
  if (score >= 60) return { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-300' };
  if (score >= 40) return { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' };
  return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' };
};

const ToolHealthBadge: React.FC<ToolHealthBadgeProps> = ({ score = 0, size = 'sm', showLabel = false }) => {
  const grade = getGrade(score);
  const color = getColor(score);

  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  const iconSizes = { sm: 12, md: 14, lg: 16 };

  return (
    <div
      className={`inline-flex items-center gap-1 rounded-full border ${color.bg} ${color.text} ${color.border} ${sizeClasses[size]} font-semibold`}
      title={`Health Score: ${score}/100 (Grade: ${grade})`}
    >
      <Shield size={iconSizes[size]} />
      <span>{grade}</span>
      {showLabel && <span className="font-normal ml-0.5">{score}</span>}
    </div>
  );
};

export default ToolHealthBadge;
