import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { RestaurantCard } from './components/RestaurantCard';
import { Filters } from './components/Filters';
import { Restaurant, PriceFilter, TimeFilter, StarFilter } from './types';
import { restaurantService } from './services/restaurantService';

function App() {
  const [priceFilter, setPriceFilter] = useState<PriceFilter>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>({ openTime: null, closeTime: null });
  const [starFilter, setStarFilter] = useState<StarFilter>(null);
  const [search, setSearch] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

  const handleImageError = (restaurantId: string) => {
    setImageErrors(prev => new Set([...prev, restaurantId]));
  };

  useEffect(() => {
    const fetchCachedRestaurants = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('🔄 Fetching cached restaurants...');
        const cachedData = await restaurantService.getCachedRestaurants();
        console.log('📦 Got cached data:', cachedData);
        
        if (cachedData && cachedData.length > 0) {
          console.log('✅ Setting restaurants:', cachedData);
          setRestaurants(cachedData);
        } else {
          console.log('⚠️ No cached restaurants found');
          setError('No restaurants found. Try searching for restaurants in your area.');
        }
      } catch (err) {
        console.error('❌ Error in fetchCachedRestaurants:', err);
        setError('Failed to fetch restaurants. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCachedRestaurants();
  }, []);

  const handleSearch = async () => {
    if (!search.trim()) {
      setError('Please enter a search term');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await restaurantService.searchRestaurants({
        term: search.trim(),
        location: '1478 Thunderbird Ave, Sunnyvale, CA',
        price: priceFilter && priceFilter.length > 0 ? priceFilter[0] : undefined,
        open_now: timeFilter.openTime || timeFilter.closeTime ? false : undefined
      });
      setRestaurants(data);
    } catch (err) {
      setError('Failed to fetch restaurants. Please try again later.');
      console.error('Error searching restaurants:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredRestaurants = restaurants.filter((restaurant) => {
    if (priceFilter && restaurant.price !== priceFilter) {
      return false;
    }

    if (starFilter && restaurant.rating < starFilter) {
      return false;
    }

    if (timeFilter.openTime || timeFilter.closeTime) {
      const hours = restaurant.operating_hours;
      if (!hours || !hours.is_hours_verified) {
        return false;
      }

      if (timeFilter.openTime && (!hours.time_open || hours.time_open < timeFilter.openTime)) {
        return false;
      }

      if (timeFilter.closeTime && (!hours.time_closed || hours.time_closed > timeFilter.closeTime)) {
        return false;
      }
    }

    return true;
  }).sort((a, b) => {
    // Sort restaurants with valid images to the top
    const aHasValidImage = a.photos && a.photos.length > 0 && !imageErrors.has(a.business_id);
    const bHasValidImage = b.photos && b.photos.length > 0 && !imageErrors.has(b.business_id);
    if (aHasValidImage && !bHasValidImage) return -1;
    if (!aHasValidImage && bHasValidImage) return 1;
    return 0;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-baseline gap-6">
            <h1 className="text-3xl font-bold">
              <span className="bg-gradient-to-r from-red-500 to-pink-500 text-transparent bg-clip-text">
                Hungry Monkey
              </span>
            </h1>
            <h2 className="text-xl text-gray-600">Holiday Restaurant Finder</h2>
          </div>
          <div className="mt-4 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search restaurants or cuisines..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </header>

      <Filters
        priceFilter={priceFilter}
        setPriceFilter={setPriceFilter}
        timeFilter={timeFilter}
        setTimeFilter={setTimeFilter}
        starFilter={starFilter}
        setStarFilter={setStarFilter}
      />

      <main className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-500 text-lg mt-4">Loading restaurants...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-500 text-lg">{error}</p>
          </div>
        ) : filteredRestaurants.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No restaurants found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRestaurants.map((restaurant) => (
              <RestaurantCard 
                key={restaurant.business_id} 
                restaurant={restaurant}
                onImageError={() => handleImageError(restaurant.business_id)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;