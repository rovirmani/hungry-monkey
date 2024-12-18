No need for supabase client

- Don't reopen supabase connections
- Supabase init should be a simple function called in VAPI Client 
- Just make sure that you don't have to reopen a connection each time you call a function

What to keep:
- in clients, keep vapi, yelp, google_custom_search

Figure out why there are two auth modules (middleware and clerk)


This should not be in DB layer but in the route calling a client :
 restaurants = await self.yelp.search_businesses(
            term=params.term,
            location=params.location,
            price=params.price,
            categories=params.categories,
            limit=params.limit,
            sort_by=params.sort_by
        )

Have a human understanding of what each folder is for. If I am doing too much in a certain function, figure out what that layer is for. 
Client and DB should be self-contained, both being called from the routes. 