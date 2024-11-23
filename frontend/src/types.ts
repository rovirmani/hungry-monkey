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
  operating_hours?: OperatingHours;
}

export interface DayHours {
  day: string;
  open: string;
  close: string;
}

export interface OperatingHours {
  time_open: string | null;
  time_closed: string | null;
  is_hours_verified: boolean;
  is_consenting: boolean;
}

export type PriceFilter = '$' | '$$' | '$$$' | '$$$$' | null;
export interface TimeFilter {
  openTime: string | null;
  closeTime: string | null;
}
export type StarFilter = 1 | 2 | 3 | 4 | 5 | null;