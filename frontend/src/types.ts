export interface Restaurant {
    id: string;
    name: string;
    image: string;
    rating: number;
    price: '$' | '$$' | '$$$' | '$$$$';
    cuisine: string;
    address: string;
    hours: DayHours[];
  }
  
  export interface DayHours {
    day: string;
    open: string;
    close: string;
  }
  
  export type PriceFilter = '$' | '$$' | '$$$' | '$$$$' | null;
  export type TimeFilter = 'now' | 'lunch' | 'dinner' | null;
  