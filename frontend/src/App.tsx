import { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
<<<<<<< HEAD
import { SignIn, SignUp, UserButton } from '@clerk/clerk-react';
=======
import { SignIn, SignUp, UserButton, useAuth } from '@clerk/clerk-react';
>>>>>>> origin
import { Search } from 'lucide-react';
import { RestaurantCard } from './components/RestaurantCard';
import { Filters } from './components/Filters';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Profile } from './pages/Profile';
import { Restaurant, PriceFilter, TimeFilter, StarFilter } from './types';
import { useRestaurantService } from './services/restaurantService';

function App() {
<<<<<<< HEAD
  const restaurantService = useRestaurantService();
  const [priceFilter, setPriceFilter] = useState<PriceFilter>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>({ openTime: null, closeTime: null });
  const [starFilter, setStarFilter] = useState<StarFilter>(null);
=======
  const { isSignedIn } = useAuth();
  const restaurantService = useRestaurantService();
  const [priceFilter, setPriceFilter] = useState<PriceFilter>(undefined);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>({ openTime: null, closeTime: null });
  const [starFilter, setStarFilter] = useState<StarFilter>(undefined);
>>>>>>> origin
  const [search, setSearch] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load cached restaurants on component mount
  useEffect(() => {
    const loadCachedRestaurants = async () => {
      try {
        setLoading(true);
        setError(null);
<<<<<<< HEAD
        const data = await restaurantService.getCachedRestaurants(undefined, false); // fetch images without auth
        setRestaurants(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load restaurants');
=======
        const data = await restaurantService.getCachedRestaurants();
        setRestaurants(data);
      } catch (err) {
        // Don't set error for empty results
        console.error('Error loading restaurants:', err);
>>>>>>> origin
      } finally {
        setLoading(false);
      }
    };

    loadCachedRestaurants();
<<<<<<< HEAD
  }, [restaurantService]);
=======
  }, []);
>>>>>>> origin

  const handleSearch = async () => {
    if (!search.trim()) {
      setError('Please enter a search term');
      return;
    }

<<<<<<< HEAD
=======
    if (!isSignedIn) {
      setError('Please sign in to search for restaurants');
      return;
    }

>>>>>>> origin
    try {
      setLoading(true);
      setError(null);
      const data = await restaurantService.searchRestaurants({
        term: search.trim(),
        location: search.trim(),
<<<<<<< HEAD
        price: priceFilter,
        open_now: timeFilter.openTime !== null
=======
        price: priceFilter
>>>>>>> origin
      });
      setRestaurants(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const filteredRestaurants = restaurants.filter(restaurant => {
    if (priceFilter && restaurant.price !== priceFilter) {
      return false;
    }

    if (timeFilter.openTime && timeFilter.closeTime) {
      // Add time filtering logic here if needed
      return true;
    }

    if (starFilter && restaurant.rating < starFilter) {
      return false;
    }

    return true;
  }).sort((a, b) => b.rating - a.rating);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex space-x-4">
            <Link to="/" className="text-gray-700 hover:text-gray-900">Home</Link>
            <Link to="/profile" className="text-gray-700 hover:text-gray-900">Profile</Link>
          </div>
          <UserButton afterSignOutUrl="/" />
        </div>
      </nav>

      <div className="container mx-auto py-8">
        <Routes>
          <Route path="/sign-in/*" element={<SignIn routing="path" path="/sign-in" />} />
          <Route path="/sign-up/*" element={<SignUp routing="path" path="/sign-up" />} />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          <Route path="/" element={
            <div>
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
                        placeholder="Enter a location to search for restaurants..."
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
                      />
                    ))}
                  </div>
                )}
              </main>
            </div>
          } />
        </Routes>
      </div>
    </div>
  );
}

export default App;