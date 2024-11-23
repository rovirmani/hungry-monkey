import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { RestaurantCard } from './components/RestaurantCard';
import { Filters } from './components/Filters';
import { Restaurant, PriceFilter, TimeFilter } from './types';
import { restaurantService } from './services/restaurantService';

function App() {
  const [priceFilter, setPriceFilter] = useState<PriceFilter>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>(null);
  const [search, setSearch] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        open_now: timeFilter === 'now'
      });
      setRestaurants(data);
    } catch (err) {
      setError('Failed to fetch restaurants. Please try again later.');
      console.error('Error searching restaurants:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredRestaurants = restaurants.filter(restaurant => {
    const matchesPrice = !priceFilter || restaurant.price === priceFilter;
    const matchesSearch = !search || 
                         restaurant.name.toLowerCase().includes(search.toLowerCase()) ||
                         restaurant.categories.some(category => 
                           category.title.toLowerCase().includes(search.toLowerCase())
                         );
    
    let matchesTime = true;
    if (timeFilter) {
      const today = new Date().getDay();
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const todayHours = restaurant.hours?.find(h => h.day === dayNames[today]);
      
      if (todayHours) {
        const now = new Date();
        const currentHour = now.getHours();
        const [openHour] = todayHours.open.split(':').map(Number);
        const [closeHour] = todayHours.close.split(':').map(Number);

        switch (timeFilter) {
          case 'now':
            matchesTime = currentHour >= openHour && currentHour < closeHour;
            break;
          case 'lunch':
            matchesTime = openHour <= 11 && closeHour >= 15;
            break;
          case 'dinner':
            matchesTime = openHour <= 17 && closeHour >= 22;
            break;
        }
      } else {
        matchesTime = false;
      }
    }

    return matchesPrice && matchesSearch && matchesTime;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Restaurant Finder</h1>
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
              <RestaurantCard key={restaurant.business_id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;