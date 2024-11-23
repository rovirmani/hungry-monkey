import { Clock, DollarSign } from 'lucide-react';
import { PriceFilter, TimeFilter } from '../types';
import clsx from 'clsx';

interface Props {
  priceFilter: PriceFilter;
  setPriceFilter: (price: PriceFilter) => void;
  timeFilter: TimeFilter;
  setTimeFilter: (time: TimeFilter) => void;
}

export function Filters({ priceFilter, setPriceFilter, timeFilter, setTimeFilter }: Props) {
  const prices: ('$' | '$$' | '$$$' | '$$$$')[] = ['$', '$$', '$$$', '$$$$'];
  const times: { value: TimeFilter; label: string }[] = [
    { value: 'now', label: 'Open Now' },
    { value: 'lunch', label: 'Lunch (11AM-3PM)' },
    { value: 'dinner', label: 'Dinner (5PM-10PM)' }
  ];

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
              {times.map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => setTimeFilter(timeFilter === value ? null : value)}
                  className={clsx(
                    'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                    timeFilter === value
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}