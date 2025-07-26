// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Campaign types
export interface Campaign {
  id: string
  name: string
  description: string
  keywords: string[]
  status: 'active' | 'paused' | 'completed' | 'draft'
  created_at: string
  updated_at: string
  total_blogs: number
  comments_generated: number
  comments_posted: number
  success_rate: number
  settings: CampaignSettings
}

export interface CampaignSettings {
  max_blogs_per_keyword: number
  min_blog_quality_score: number
  comment_style: 'professional' | 'casual' | 'technical'
  auto_post: boolean
  posting_delay: number // in seconds
  target_domains?: string[]
  excluded_domains?: string[]
}

export interface CreateCampaignRequest {
  name: string
  description: string
  keywords: string[]
  settings: CampaignSettings
}

// Blog types
export interface Blog {
  id: string
  url: string
  title: string
  domain: string
  content_snippet: string
  keywords: string[]
  quality_score: number
  seo_score: number
  readability_score: number
  authority_score: number
  comment_opportunity_score: number
  discovered_at: string
  last_analyzed: string
  status: 'discovered' | 'analyzed' | 'approved' | 'commented' | 'rejected'
  rejection_reason?: string
  campaign_id: string
}

export interface BlogSearchRequest {
  keywords: string[]
  max_results?: number
  min_quality_score?: number
  excluded_domains?: string[]
  target_domains?: string[]
}

export interface BlogAnalysis {
  content_quality: {
    score: number
    factors: {
      word_count: number
      readability: number
      structure: number
      engagement: number
    }
  }
  seo_analysis: {
    score: number
    factors: {
      title_optimization: number
      meta_description: number
      keyword_density: number
      internal_links: number
      external_links: number
    }
  }
  comment_opportunity: {
    score: number
    factors: {
      comment_section_exists: boolean
      recent_comments: number
      engagement_level: number
      moderation_level: string
    }
  }
  domain_authority: {
    score: number
    metrics: {
      domain_age: number
      backlink_count: number
      traffic_estimate: number
      social_signals: number
    }
  }
}

// Comment types
export interface Comment {
  id: string
  blog_id: string
  campaign_id: string
  content: string
  style: 'professional' | 'casual' | 'technical'
  status: 'generated' | 'approved' | 'posted' | 'failed' | 'rejected'
  generated_at: string
  posted_at?: string
  author_name: string
  author_email: string
  author_website?: string
  post_response?: {
    success: boolean
    response_code?: number
    response_message?: string
  }
}

export interface CommentGenerationRequest {
  blog_id: string
  style: 'professional' | 'casual' | 'technical'
  author_persona?: {
    name: string
    email: string
    website?: string
    expertise_area?: string
  }
  custom_instructions?: string
}

// Analytics types
export interface DashboardStats {
  active_campaigns: number
  total_blogs_discovered: number
  comments_generated: number
  comments_posted: number
  success_rate: number
  avg_quality_score: number
}

export interface CampaignAnalytics {
  campaign_id: string
  date_range: {
    start: string
    end: string
  }
  metrics: {
    blogs_discovered: number
    blogs_analyzed: number
    comments_generated: number
    comments_posted: number
    success_rate: number
    quality_distribution: {
      high: number // 80-100
      medium: number // 60-79
      low: number // <60
    }
  }
  trends: {
    daily_discovery: Array<{
      date: string
      count: number
    }>
    daily_comments: Array<{
      date: string
      generated: number
      posted: number
    }>
  }
}

export interface PerformanceMetrics {
  total_processing_time: number
  avg_blog_analysis_time: number
  avg_comment_generation_time: number
  avg_posting_time: number
  error_rate: number
  api_costs: {
    total: number
    breakdown: {
      vertex_ai: number
      web_scraping: number
      other: number
    }
  }
}

// Settings types
export interface UserSettings {
  profile: {
    name: string
    email: string
    company?: string
  }
  api_keys: {
    vertex_ai?: string
    serp_api?: string
    custom_scraping?: string
  }
  default_author_personas: Array<{
    id: string
    name: string
    email: string
    website?: string
    expertise_area?: string
    is_default: boolean
  }>
  notification_preferences: {
    email_notifications: boolean
    campaign_completion: boolean
    error_alerts: boolean
    daily_summary: boolean
  }
  posting_settings: {
    default_delay: number
    max_posts_per_day: number
    respect_robots_txt: boolean
    user_agent: string
  }
}

// Error types
export interface AppError {
  code: string
  message: string
  details?: Record<string, unknown>
  timestamp: string
}

// Form types
export interface FormFieldError {
  message: string
}

export interface FormErrors {
  [key: string]: FormFieldError | undefined
}

// Navigation types
export interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  current: boolean
}
