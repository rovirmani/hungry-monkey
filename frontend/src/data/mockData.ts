import { Restaurant } from '../types';

export const restaurants: Restaurant[] = [
  {
    id: '1',
    name: 'The Rustic Table',
    image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
    rating: 4.5,
    price: '$$',
    cuisine: 'American',
    address: '123 Main St, Anytown, USA',
    hours: [
      { day: 'Monday', open: '11:00', close: '22:00' },
      { day: 'Tuesday', open: '11:00', close: '22:00' },
      { day: 'Wednesday', open: '11:00', close: '22:00' },
      { day: 'Thursday', open: '11:00', close: '23:00' },
      { day: 'Friday', open: '11:00', close: '23:00' },
      { day: 'Saturday', open: '10:00', close: '23:00' },
      { day: 'Sunday', open: '10:00', close: '21:00' }
    ]
  },
  {
    id: '2',
    name: 'Sakura Sushi',
    image: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80',
    rating: 4.8,
    price: '$$$',
    cuisine: 'Japanese',
    address: '456 Cherry Blossom Lane, Anytown, USA',
    hours: [
      { day: 'Monday', open: '12:00', close: '22:30' },
      { day: 'Tuesday', open: '12:00', close: '22:30' },
      { day: 'Wednesday', open: '12:00', close: '22:30' },
      { day: 'Thursday', open: '12:00', close: '23:00' },
      { day: 'Friday', open: '12:00', close: '23:30' },
      { day: 'Saturday', open: '13:00', close: '23:30' },
      { day: 'Sunday', open: '13:00', close: '22:00' }
    ]
  },
  {
    id: '3',
    name: 'La Piazza',
    image: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
    rating: 4.6,
    price: '$$$$',
    cuisine: 'Italian',
    address: '789 Olive Garden Way, Anytown, USA',
    hours: [
      { day: 'Monday', open: '17:00', close: '23:00' },
      { day: 'Tuesday', open: '17:00', close: '23:00' },
      { day: 'Wednesday', open: '17:00', close: '23:00' },
      { day: 'Thursday', open: '17:00', close: '23:30' },
      { day: 'Friday', open: '17:00', close: '00:00' },
      { day: 'Saturday', open: '16:00', close: '00:00' },
      { day: 'Sunday', open: '16:00', close: '22:00' }
    ]
  }
];