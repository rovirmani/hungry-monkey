import { Star } from 'lucide-react';
import { Restaurant } from '../types';

interface Props {
  restaurant: Restaurant;
}

export function RestaurantCard({ restaurant }: Props) {
  const googleMapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    restaurant.location.display_address.join(', ')
  )}`;

  const yelpLink = `https://www.yelp.com/biz/${restaurant.business_id}`;

  // Use the image URL directly since we're getting them from Google Search now
  const imageUrl = restaurant.photos && restaurant.photos.length > 0
    ? restaurant.photos[0]
    : '/placeholder-restaurant.jpg';

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-[1.02] hover:shadow-lg">
      <img 
        src={imageUrl}
        alt={restaurant.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <a 
            href={yelpLink}
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-xl font-semibold hover:text-blue-600 transition-colors"
          >
            {restaurant.name}
          </a>
          {restaurant.price && (
            <span className="px-2 py-1 bg-gray-100 rounded-full text-sm">
              {restaurant.price}
            </span>
          )}
        </div>
        
        <div className="flex items-center mb-2">
          <Star className="w-4 h-4 fill-yellow-400 stroke-yellow-400 mr-1" />
          <span className="text-sm text-gray-600">{restaurant.rating}</span>
          {restaurant.categories.length > 0 && (
            <>
              <span className="mx-2">•</span>
              <span className="text-sm text-gray-600">
                {restaurant.categories.map(cat => cat.title).join(', ')}
              </span>
            </>
          )}
        </div>

        <a 
          href={googleMapsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-gray-500 hover:text-blue-600 mb-2 block"
        >
          {restaurant.location.display_address.join(', ')}
        </a>
        
        {restaurant.hours && restaurant.hours.length > 0 && (
          <div className="text-sm">
            <span className="font-medium">Hours:</span>
            <span className="ml-2 text-gray-600">
              {restaurant.is_open ? 'Open Now' : 'Closed'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}