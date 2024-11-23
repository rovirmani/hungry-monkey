import { useState } from 'react';
import { Search } from 'lucide-react';
import { RestaurantCard } from './components/RestaurantCard';
import { Filters } from './components/Filters';
import { restaurants } from './data/mockData';
import { PriceFilter, TimeFilter } from './types';

function App() {
  const [priceFilter, setPriceFilter] = useState<PriceFilter>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>(null);
  const [search, setSearch] = useState('');

  const filteredRestaurants = restaurants.filter(restaurant => {
    const matchesPrice = !priceFilter || restaurant.price === priceFilter;
    const matchesSearch = restaurant.name.toLowerCase().includes(search.toLowerCase()) ||
                         restaurant.cuisine.toLowerCase().includes(search.toLowerCase());
    
    let matchesTime = true;
    if (timeFilter) {
      const today = new Date().getDay();
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const todayHours = restaurant.hours.find(h => h.day === dayNames[today]);
      
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
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search restaurants or cuisines..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
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
        {filteredRestaurants.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No restaurants found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRestaurants.map(restaurant => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;