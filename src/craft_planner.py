import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        #Check requirements
        for item, condition in rule['Requires']:
            if state[item] != condition:
                return False

        #Check consumption requirements
        for item, condition in rule['Consumes']:
            if state[item] >= condition:
                return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].

        #Check consumption requirements
        next_state = state.copy()
        for item, num_consumed in rule['Consumes']:
            next_state[item] -= num_consumed

        for item, num_produced in rule['Produces']:
            next_state[item] += num_produced

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        goalItem, goalAmount = goal
        if state[goalItem] == goalAmount:
            return True
        return False

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit:
        pass

    explored_states = dict()
    frontQueue = []
    heappush(frontQueue, (0, state))

    came_from = dict()
    cost_so_far = dict()
    action_to_state = dict()

    action_to_state[state] = None
    came_from[state] = None
    cost_so_far[state] = 0

    while frontQueue > 0:
        p1, current_state = heappop(frontQueue)
        explored_states[state] = True

    #----------------------------------------------------------------
    #is what happens if we find destination
        if is_goal(state):
            pathCells = []
            cs = current_state
            action = action_to_state[cs] #action that leads up to our current state
            pathCells.append((cs, action))
            while cs is not None:
                action = action_to_state[came_from[cs]] #action to lead up to previous state
                pathCells.append((came_from[cs], action)) #append previous state and the action
                cs = came_from[cs] #go back one
            return pathCells
    #-----------------------------------------------------------------

        for name, new_state, cost in graph(current_state):
            cost = heuristic(new_state, name)
            new_cost = cost_so_far[current_state] + cost
            if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                cost_so_far[new_state] = new_cost
                priority = new_cost
                heappush(frontQueue, (priority, new_state))
                came_from[new_state] = current_state
                action_to_state[new_state] = name

#in the case that it exits but no path is found
return None

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 5, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
