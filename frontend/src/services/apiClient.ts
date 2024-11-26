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
        console.log('Token received:', token ? token.substring(0, 20) + '...' : 'No token');
        if (!token) {
          throw new Error('Authentication required but no token available');
        }
        headers['Authorization'] = `Bearer ${token}`;
        console.log('Authorization header:', headers['Authorization'].substring(0, 30) + '...');
      }

      return client.request<T>(endpoint, {
        method: 'GET',
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
        console.log('Token received:', token ? token.substring(0, 20) + '...' : 'No token');
        if (!token) {
          throw new Error('Authentication required but no token available');
        }
        headers['Authorization'] = `Bearer ${token}`;
        console.log('Authorization header:', headers['Authorization'].substring(0, 30) + '...');
      }

      return client.request<T>(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
    }
  };
};
