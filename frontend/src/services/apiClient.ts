class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    // Remove any trailing slashes from the base URL
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Ensure endpoint starts with a slash
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${this.baseUrl}${normalizedEndpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
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
