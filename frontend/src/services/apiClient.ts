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
    const response = await fetch(url, options);
    
    if (!response.ok) {
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
        const token = await getToken();
        if (!token) {
          throw new Error('Authentication required but no token available');
        }
        headers['Authorization'] = `Bearer ${token}`;
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
        const token = await getToken();
        if (!token) {
          throw new Error('Authentication required but no token available');
        }
        headers['Authorization'] = `Bearer ${token}`;
      }

      return client.request<T>(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
    }
  };
};
