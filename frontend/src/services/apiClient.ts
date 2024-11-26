class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    console.log('Making request to:', url);
    console.log('Request options:', {
      ...options,
      headers: options.headers
    });
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
      console.error('Request failed:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });
      const errorText = await response.text();
      console.error('Error response:', errorText);
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
