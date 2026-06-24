import { createBrowserClient } from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface FetchOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  requireAuth?: boolean;
}

export class APIFetcher {
  private static getSupabaseClient() {
    return createBrowserClient(supabaseUrl, supabaseAnonKey)
  }

  private static async getAuthToken(): Promise<string | null> {
    const supabase = this.getSupabaseClient();
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  }

  static async fetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { 
      timeout = 8000, 
      retries = 2, 
      requireAuth = true,
      ...customConfig 
    } = options;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...customConfig.headers,
    };

    if (requireAuth) {
      const token = await this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        throw new Error('Authentication required but no token found.');
      }
    }

    const config: RequestInit = {
      ...customConfig,
      headers,
    };

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    config.signal = controller.signal;

    let attempt = 0;
    while (attempt <= retries) {
      try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        clearTimeout(id);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json() as T;
      } catch (error: any) {
        if (error.name === 'AbortError') {
          throw new Error('Request timed out');
        }
        
        attempt++;
        if (attempt > retries) {
          throw error;
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt - 1)));
      }
    }
    throw new Error('Unreachable code');
  }

  // Convenience methods
  static get<T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) {
    return this.fetch<T>(endpoint, { ...options, method: 'GET' });
  }

  static post<T>(endpoint: string, data: any, options?: Omit<FetchOptions, 'method' | 'body'>) {
    return this.fetch<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(data) });
  }

  static put<T>(endpoint: string, data: any, options?: Omit<FetchOptions, 'method' | 'body'>) {
    return this.fetch<T>(endpoint, { ...options, method: 'PUT', body: JSON.stringify(data) });
  }

  static delete<T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) {
    return this.fetch<T>(endpoint, { ...options, method: 'DELETE' });
  }
}
