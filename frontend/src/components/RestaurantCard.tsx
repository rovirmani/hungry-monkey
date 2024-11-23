import { Star } from 'lucide-react';
import { Restaurant } from '../types';
import { useState, useEffect } from 'react';

interface Props {
  restaurant: Restaurant;
  onImageError: () => void;
}

export function RestaurantCard({ restaurant, onImageError }: Props) {
  const [imageLoadError, setImageLoadError] = useState(false);
  
  const googleMapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    restaurant.location.display_address.join(', ')
  )}`;

  const yelpLink = `https://www.yelp.com/biz/${restaurant.business_id}`;

  const hasImage = restaurant.photos && restaurant.photos.length > 0 && !imageLoadError;
  const imageUrl = hasImage ? restaurant.photos[0] : '/placeholder-restaurant.jpg';

  const handleImageError = () => {
    setImageLoadError(true);
    onImageError();
  };

  const getHoursDisplay = () => {
    if (!restaurant.operating_hours) {
      return <span className="text-gray-500 text-sm">Searching for hours...</span>;
    }

    if (!restaurant.operating_hours.is_hours_verified) {
      return <span className="text-gray-500 text-sm">Verifying hours...</span>;
    }

    if (restaurant.operating_hours.time_open && restaurant.operating_hours.time_closed) {
      return <span className="text-sm">Open: {restaurant.operating_hours.time_open} - {restaurant.operating_hours.time_closed}</span>;
    }

    return <span className="text-gray-500 text-sm">Hours unavailable</span>;
  };

  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-[1.02] hover:shadow-lg ${!hasImage ? 'border border-gray-200' : ''}`}>
      {hasImage && (
        <div className="w-full h-48 bg-gray-800">
          <img 
            src={imageUrl}
            alt={restaurant.name}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex flex-col gap-2">
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
          <div className="flex items-center gap-0">
                  {getHoursDisplay()}
                </div>
          <div className="flex items-center gap-2">
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
      </div>
    </div>
  );
}