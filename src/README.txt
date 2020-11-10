Names:
Darcy Phipps
Darrion Nguyen

SEARCH ALGORITHM:
So we used the a similar approach to the A* implementation for our search. We use dictionaries to keep track of what action led to what state, the parent of each state,
and the cost so far to reach that state. We use the state itself as the key for all these dictionaries. 

Just like before, we used a priority queue in order to prioritize the shortest path so far first. As a state is popped from the queue, we check if it is the goal state, 
and if it is we backtrack through parents to organize the path to return to the main function.

Otherwise, we look through the neighbors of the state, which are any available new states that can be accessed from our current one. We calculate the cost to reach the new state,
and if it is less than anything we found so far, or it is the only existent path, then we calculate the cost + the heuristic and add it to the queue setting any dictionaries as necessary. 
The heuristic determines whether or not we should pursue this route with priority.

HEURISTIC:
Unlike A* though, our heuristic does not necessarily predict the distance between our current state and the goal state, but rather is used only to prune routes that are 
impossible to yield results. We do this by checking the goal state, and seeing if any of the resources are required as a goal. If it is, then the max amount of that resource
we would ever need is a max function of that goal, or the max amount of that resource we need to build the most complicated item. We use this heuristic on wood,sticks, planks
cobble, ingot, cart, ore, and coal. The intuition behind this is that we can always gather more resources as we come along, but any extra resource is unneeded so it is better to cap it.

An additional heuristic is that we only need one of each tool, so the algorithm will disregard building more. It also makes sure when we have a better tool, it would never use the worst 
one as that will always be slower.

Finally some resources are used only to be crafted, so we made sure that those resources are always crafted and that we do not need any more than necessary. For example, wood is always turned
into planks so we never allow for more than one piece of wood, and anytime we do have wood we instantly turn it into planks. This also applies to ores and coal.