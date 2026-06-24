import { createBrowserClient } from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const getSupabaseBrowserClient = () => {
  return createBrowserClient(supabaseUrl, supabaseAnonKey)
}

export class AuthClient {
  static async getUser() {
    const supabase = getSupabaseBrowserClient()
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error) throw error
    return user
  }

  static async getSession() {
    const supabase = getSupabaseBrowserClient()
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) throw error
    return session
  }

  static async signOut() {
    const supabase = getSupabaseBrowserClient()
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }
  
  static async refreshSession() {
    const supabase = getSupabaseBrowserClient()
    const { data: { session }, error } = await supabase.auth.refreshSession()
    if (error) throw error
    return session
  }
}
