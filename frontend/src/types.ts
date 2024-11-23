export interface Restaurant {
  business_id: string;
  name: string;
  rating: number;
  price?: string;
  phone?: string;
  location: {
    address1: string;
    address2?: string;
    address3?: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
    display_address: string[];
  };
  coordinates: {
    latitude: number;
    longitude: number;
  };
  photos: string[];
  categories: Array<{
    alias: string;
    title: string;
  }>;
  is_open: boolean;
  hours?: DayHours[];
}

export interface DayHours {
  day: string;
  open: string;
  close: string;
}

export type PriceFilter = '$' | '$$' | '$$$' | '$$$$' | null;
export type TimeFilter = 'now' | 'lunch' | 'dinner' | null;