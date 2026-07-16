export type StudentProgram =
  | 'MBBS'
  | 'BDS'
  | 'Nursing'
  | 'Pharmacy'
  | 'Physiotherapy'
  | 'BAMS'
  | 'BHMS'

export interface User {
  id: number
  email: string
  full_name: string
  program: StudentProgram
  year_of_study: number
  avatar_url?: string
  is_active: boolean
  is_verified?: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface HealthStatus {
  status: string
  version: string
  environment: string
}
