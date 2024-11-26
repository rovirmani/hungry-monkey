class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    // Remove any trailing slashes from the base URL
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    console.log('🔧 API Client initialized with base URL:', this.baseUrl);
    console.log('📝 Environment:', {
      isDevelopment: import.meta.env.DEV,
      isProduction: import.meta.env.PROD,
      mode: import.meta.env.MODE,
      baseUrl: import.meta.env.VITE_API_URL
    });
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Ensure endpoint starts with a slash
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${this.baseUrl}${normalizedEndpoint}`;
    
    console.log(`🔍 Making request to: ${url}`, {
      baseUrl: this.baseUrl,
      endpoint: normalizedEndpoint,
      fullUrl: url
    });
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      // Log response details
      console.log(`📡 Response status: ${response.status} ${response.statusText}`);
      console.log(`📋 Response headers:`, Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        let errorMessage = `API call failed: ${response.statusText}`;
        
        try {
          if (contentType?.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail?.message || errorData.detail || errorMessage;
          } else {
            const errorText = await response.text();
            console.error('Non-JSON error response:', errorText);
            errorMessage = `API returned non-JSON response: ${response.status} ${response.statusText}`;
          }
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Request failed:', {
        url,
        error,
        baseUrl: this.baseUrl,
        endpoint: normalizedEndpoint
      });
      throw error;
    }
  }
}

export const createAuthenticatedClient = (baseUrl: string, getToken: () => Promise<string | null>) => {
  const client = new ApiClient(baseUrl);

  return {
    async get<T>(endpoint: string, requiresAuth: boolean = false): Promise<T> {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (requiresAuth) {
        console.log('Getting token for authenticated request...');
        const token = await getToken();
        if (token) {
          console.log('Token received (first 50 chars):', token.substring(0, 50));
          try {
            // Log token claims for debugging (base64 decode the payload)
            const [, payload] = token.split('.');
            const claims = JSON.parse(atob(payload));
            console.log('Token claims:', claims);
          } catch (e) {
            console.error('Error decoding token:', e);
          }
        } else {
          console.warn('No token received');
        }
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }

      return client.request<T>(endpoint, {
        headers,
      });
    },

    async post<T>(endpoint: string, data: any, requiresAuth: boolean = false): Promise<T> {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (requiresAuth) {
        console.log('Getting token for authenticated request...');
        const token = await getToken();
        if (token) {
          console.log('Token received (first 50 chars):', token.substring(0, 50));
          try {
            // Log token claims for debugging (base64 decode the payload)
            const [, payload] = token.split('.');
            const claims = JSON.parse(atob(payload));
            console.log('Token claims:', claims);
          } catch (e) {
            console.error('Error decoding token:', e);
          }
        } else {
          console.warn('No token received');
        }
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }

      return client.request<T>(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
    },
  };
};
