import { Restaurant } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/restaurants';  // adjust this to match your backend URL

// Convert frontend price format to backend format
function convertPriceFilter(price: string | null): string | undefined {
  if (!price) return undefined;
  return price.length.toString();
}

// Helper function to transform backend restaurant data to frontend format
function transformRestaurant(backendRestaurant: any): Restaurant {
  console.log('🔄 Transforming restaurant:', backendRestaurant);
  
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
    is_open: backendRestaurant.is_open ?? true
  };
  
  console.log('✅ Transformed restaurant:', transformed);
  return transformed;
}

export const restaurantService = {
  async searchRestaurants(params: {
    term?: string;
    location: string;
    price?: string;
    open_now?: boolean;
    categories?: string;
  }): Promise<Restaurant[]> {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        if (key === 'price' && typeof value === 'string') {
          const backendPrice = convertPriceFilter(value);
          if (backendPrice) {
            queryParams.append(key, backendPrice);
          }
        } else if (key === 'open_now' && typeof value === 'boolean') {
          queryParams.append(key, value.toString());
        } else if (typeof value === 'string') {
          queryParams.append(key, value);
        }
      }
    });

    try {
      console.log('🔍 Searching restaurants with params:', params);
      const response = await fetch(`${API_BASE_URL}/search?${queryParams}`);
      if (!response.ok) {
        throw new Error('Failed to fetch restaurants');
      }
      const data = await response.json();
      console.log('📦 Got restaurant data:', data);
      return data.map(transformRestaurant);
    } catch (error) {
      console.error('❌ Error fetching restaurants:', error);
      throw error;
    }
  },

  async getRestaurantDetails(businessId: string): Promise<Restaurant> {
    try {
      console.log('🔍 Getting restaurant details for ID:', businessId);
      const response = await fetch(`${API_BASE_URL}/${businessId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('📦 Got restaurant details:', data);
      return transformRestaurant(data);
    } catch (error) {
      console.error('❌ Error fetching restaurant details:', error);
      throw new Error('Failed to fetch restaurant details');
    }
  },

  async getCachedRestaurants(limit?: number): Promise<Restaurant[]> {
    try {
      console.log('🔍 Getting cached restaurants...');
      const queryParams = new URLSearchParams();
      if (limit) {
        queryParams.append('limit', limit.toString());
      }
      // Always fetch images for restaurants that don't have them
      queryParams.append('fetch_images', 'true');
      
      const response = await fetch(`${API_BASE_URL}/cached?${queryParams}`);
      if (!response.ok) {
        throw new Error('Failed to fetch cached restaurants');
      }
      const data = await response.json();
      console.log('📦 Got cached restaurant data:', data);
      return data.map(transformRestaurant);
    } catch (error) {
      console.error('❌ Error fetching cached restaurants:', error);
      throw error;
    }
  }
};
