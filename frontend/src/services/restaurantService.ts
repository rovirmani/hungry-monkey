import { Restaurant } from '../types';
import { createAuthenticatedClient } from './apiClient';
import { useAuth } from '@clerk/clerk-react';
import { useMemo } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL;  // Use environment variable

// Convert frontend price format to backend format
function convertPriceFilter(price: string | null): string | undefined {
  if (!price) return undefined;
  return price.length.toString();
}

// Helper function to transform backend restaurant data to frontend format
function transformRestaurant(backendRestaurant: any): Restaurant {
  console.log(' Transforming restaurant:', backendRestaurant);
  
  // Handle location data comprehensively
  const location = backendRestaurant.location || {};
  const displayAddress = location.display_address || [];
  
  // If display_address is null or empty, construct it from other location fields
  const addressParts = [
    location.address1 || '',
    location.address2 || '',
    location.address3 || '',
    location.city || '',
    location.state || '',
    location.zip_code || '',
    location.country || ''
  ].filter(Boolean); // Remove null/undefined/empty values

  const transformedLocation = {
    address1: location.address1 || '',
    address2: location.address2 || undefined,
    address3: location.address3 || undefined,
    city: location.city || '',
    state: location.state || '',
    zip_code: location.zip_code || '',
    country: location.country || '',
    display_address: displayAddress.length > 0 
      ? displayAddress 
      : addressParts.filter(part => part.trim() !== '')
  };

  const transformed = {
    business_id: backendRestaurant.business_id || backendRestaurant.id || '',
    name: backendRestaurant.name || '',
    rating: backendRestaurant.rating || 0,
    price: backendRestaurant.price || '',
    phone: backendRestaurant.phone || '',
    location: transformedLocation,
    coordinates: {
      latitude: backendRestaurant.coordinates?.latitude || 0,
      longitude: backendRestaurant.coordinates?.longitude || 0
    },
    photos: backendRestaurant.photos || [],
    categories: backendRestaurant.categories || [],
    is_open: backendRestaurant.is_open ?? true,
    operating_hours: {
      time_open: backendRestaurant.operating_hours?.time_open || null,
      time_closed: backendRestaurant.operating_hours?.time_closed || null,
      is_hours_verified: backendRestaurant.operating_hours?.is_hours_verified || false,
      is_consenting: backendRestaurant.operating_hours?.is_consenting || false,
      is_open: backendRestaurant.operating_hours?.is_open || false
    },
    is_closed: !backendRestaurant.operating_hours?.is_open
  };
  
  console.log(' Transformed restaurant:', transformed);
  return transformed;
}

export function useRestaurantService() {
  const { getToken } = useAuth();
  
  const apiClient = useMemo(() => createAuthenticatedClient(API_BASE_URL, async () => {
    try {
      const token = await getToken({
        template: "hungry-monkey-jwt"  // Use the configured template
      });
      return token;
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }), [getToken]);

  return {
    async searchRestaurants(params: {
      term?: string;
      location: string;
      price?: string;
      categories?: string;
    }): Promise<Restaurant[]> {
      const searchParams = new URLSearchParams();
      if (params.term) searchParams.append('term', params.term);
      if (params.location) searchParams.append('location', params.location);
      if (params.price) searchParams.append('price', convertPriceFilter(params.price) || '');
      if (params.categories) searchParams.append('categories', params.categories);

      const response = await apiClient.get<any>(
        `/restaurants/search?${searchParams.toString()}`,
        true
      );
      return response.map(transformRestaurant);
    },

    async getRestaurantDetails(businessId: string): Promise<Restaurant> {
      const response = await apiClient.get<any>(
        `/restaurants/${businessId}`,
        true
      );
      return transformRestaurant(response);
    },

    async getCachedRestaurants(): Promise<Restaurant[]> {
      try {
        const response = await fetch(`${API_BASE_URL}/restaurants`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.map(transformRestaurant);
      } catch (error) {
        console.error('Error fetching cached restaurants:', error);
        // Return empty array for network errors or other issues
        return [];
      }
    },

    async makeCall(phoneNumber: string, message?: string): Promise<any> {
      return apiClient.post('/vapi/call/' + phoneNumber, { message }, true);
    },

    async getCallAnalysis(callId: string): Promise<any> {
      return apiClient.get('/vapi/call-analysis/' + callId, true);
    },

    async checkHours(restaurantId: string): Promise<any> {
      return apiClient.get('/vapi/check-hours/' + restaurantId, true);
    }
  };
}
