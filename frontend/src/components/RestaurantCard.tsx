import { Star } from 'lucide-react';
import { Restaurant } from '../types';

interface Props {
  restaurant: Restaurant;
}

export function RestaurantCard({ restaurant }: Props) {
  const today = new Date().getDay();
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const todayHours = restaurant.hours.find(h => h.day === dayNames[today]);
  const googleMapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(restaurant.address)}`;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-[1.02] hover:shadow-lg">
      <img 
        src={restaurant.image} 
        alt={restaurant.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-semibold">{restaurant.name}</h3>
          <span className="px-2 py-1 bg-gray-100 rounded-full text-sm">
            {restaurant.price}
          </span>
        </div>
        
        <div className="flex items-center mb-2">
          <Star className="w-4 h-4 fill-yellow-400 stroke-yellow-400 mr-1" />
          <span className="text-sm text-gray-600">{restaurant.rating}</span>
          <span className="mx-2">•</span>
          <span className="text-sm text-gray-600">{restaurant.cuisine}</span>
        </div>

        <a 
          href={googleMapsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-gray-500 hover:text-blue-600 mb-2 block"
        >
          {restaurant.address}
        </a>
        
        <div className="text-sm">
          <span className="font-medium">Today:</span>
          <span className="ml-2 text-gray-600">
            {todayHours ? `${todayHours.open} - ${todayHours.close}` : 'Closed'}
          </span>
        </div>
      </div>
    </div>
  );
}