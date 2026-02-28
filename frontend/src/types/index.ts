export interface Tool {
  id: number;
  name: string;
  slug: string;
  description: string;
  homepage_url?: string;
  github_url?: string;
  category: string;
  license?: string;
  pricing_model: string;
  github_stars: number;
  github_forks: number;
  ai_summary?: string;
  health_score?: number;
  created_at: string;
  updated_at?: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  avatar_url?: string;
  bio?: string;
  created_at: string;
}

export interface HealthScoreBreakdown {
  score: number;
  weight: number;
}

export interface HealthScore {
  score: number;
  grade: string;
  breakdown: Record<string, HealthScoreBreakdown>;
  stars?: number;
  open_issues?: number;
  calculated_at?: string;
  error?: string;
}
