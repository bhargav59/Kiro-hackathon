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
