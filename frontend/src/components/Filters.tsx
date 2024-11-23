import { Clock, DollarSign, Star } from 'lucide-react';
import { PriceFilter, TimeFilter, StarFilter } from '../types';
import clsx from 'clsx';

interface Props {
  priceFilter: PriceFilter;
  setPriceFilter: (price: PriceFilter) => void;
  timeFilter: TimeFilter;
  setTimeFilter: (time: TimeFilter) => void;
  starFilter: StarFilter;
  setStarFilter: (stars: StarFilter) => void;
}

const generateTimeOptions = () => {
  const options = [];
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      options.push(time);
    }
  }
  return options;
};

export function Filters({ 
  priceFilter, 
  setPriceFilter, 
  timeFilter, 
  setTimeFilter,
  starFilter,
  setStarFilter 
}: Props) {
  const prices: ('$' | '$$' | '$$$' | '$$$$')[] = ['$', '$$', '$$$', '$$$$'];
  const stars: StarFilter[] = [1, 2, 3, 4, 5];
  const timeOptions = generateTimeOptions();

  return (
    <div className="sticky top-0 bg-white shadow-sm p-4 z-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-gray-500" />
            <div className="flex gap-1">
              {prices.map((price) => (
                <button
                  key={price}
                  onClick={() => setPriceFilter(priceFilter === price ? null : price)}
                  className={clsx(
                    'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                    priceFilter === price
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {price}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <div className="flex gap-1">
              <select
                className="px-3 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-200"
                value={timeFilter.openTime || ''}
                onChange={(e) => setTimeFilter({ ...timeFilter, openTime: e.target.value || null })}
              >
                <option value="">Open Time</option>
                {timeOptions.map((time) => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
              <span className="text-gray-700">to</span>
              <select
                className="px-3 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-200"
                value={timeFilter.closeTime || ''}
                onChange={(e) => setTimeFilter({ ...timeFilter, closeTime: e.target.value || null })}
              >
                <option value="">Close Time</option>
                {timeOptions.map((time) => (
                  <option key={time} value={time}>
                    {time}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Star className="w-5 h-5 text-gray-500" />
            <div className="flex gap-1">
              {stars.map((star) => (
                <button
                  key={star}
                  onClick={() => setStarFilter(starFilter === star ? null : star)}
                  className={clsx(
                    'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                    starFilter === star
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {star}+ ★
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}