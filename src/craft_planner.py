import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from math import inf
from heapq import heappop, heappush

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
        if "Requires" in rule:
            for item, condition in rule['Requires'].items():
                if state[item] != condition:
                    return False

        #Check consumption requirements
        if "Consumes" in rule:
            for item, condition in rule['Consumes'].items():
                if state[item] < condition:
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
        if "Consumes" in rule:
            for item, num_consumed in rule['Consumes'].items():
                next_state[item] -= num_consumed

        for item, num_produced in rule['Produces'].items():
            next_state[item] += num_produced

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for goalItem, goalAmount in goal.items():
            if state[goalItem] < goalAmount:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, action_name):
    # Implement your heuristic here!
    #You should never have more than 1 wood, should be turning it into planks instead
    if state["wood"] > 1:
        return inf
    #If you have wood, you should be turning it into planks
    if state["wood"] == 1 and "for wood" not in action_name:
        return inf

    #Don't need more than 8 cobble
    if state["cobble"] > 8:
        return inf

    #never need more than 6 ingot since max ingot to craft is 6 with the rails
    if state["ingot"] > 6:
        return inf

    #seems like we only need 1 cart for now suspect to change
    if state["cart"] > 1:
        return inf

    #Only check these requirements if you're crafting
    if action_name[0:5] == "craft":
        #Don't make duplicate tools
        list_of_tools = ["bench", "furnace", "wooden_pickaxe", "stone_pickaxe", "iron_pickaxe", "wooden_axe", "stone_axe", "iron_axe"]
        for tool in list_of_tools:
            if state[tool] > 1:
                return inf


        #No recipie needs more than 2 sticks, so if we have more than 4 (1 craft worth) something is bad
        if state["stick"] > 4:
            return inf

        #Don't need more planks than 1 craft makes, except that due to reasons you might need more temporarily
        if state["plank"] > 7:
            return inf
        ##If you have enough planks to make sticks, and you have made everything needing planks, make sticks instead
        #if state["bench"] and state["wooden_pickaxe"] and state["wooden_axe"] and state["plank"] > 3 and action_name != "craft plank" and action_name != "craft stick":
        #    return inf
        #check these only for benchcrafting
        if action_name[-8:] == "at bench":
            #Get shortened name
            shortened_name = action_name[6:-9]
            #Don't make worse pickaxes or axes
            if shortened_name == "wooden_axe" and state["stone_axe"]:
                #print("failaxe")
                return inf
            if (shortened_name == "stone_axe" or shortened_name == "wooden_axe") and state["iron_axe"]:
                #print("failaxe")
                return inf
            if shortened_name == "wooden_pickaxe" and state["stone_pickaxe"]:
                #print("failpick")
                return inf
            if (shortened_name == "stone_pickaxe" or shortened_name == "wooden_pickaxe") and state["iron_pickaxe"]:
                #print("failpick")
                return inf
            #At this point, if we're making a tool, priortiise it, tools are good)
        #    if "axe" in shortened_name:
            #    return -.5

    #Check to see that you never use a bad tool, or that you make a better tool instead of using a bad one
    elif "axe" in action_name:
        #check pickaxes
        if "pickaxe" in action_name:
            #The first "iron_pickaxe" in the next line should be stone instead, but this makes a better runtime
            if ("wooden_pickaxe" in action_name or "iron_pickaxe" in action_name) and (state["iron_pickaxe"] or (state["ingot"] >= 3 and state["stick"] >= 2)):
                return inf
            if "wooden_pickaxe" in action_name and (state["stone_pickaxe"] or (state["cobble"] >= 3 and state["stick"] >= 2)):
                return inf

            #Also make sure we aren't trying to get cobble if we already have everything that needs cobble
            if "cobble" in action_name and state["furnace"] and (state["stone_pickaxe"] or state["iron_pickaxe"]) and (state["stone_axe"] or state["iron_axe"]):
                return inf
        #check axes
        else:
            if ("wooden_axe" in action_name or "stone_axe" in action_name) and (state["iron_axe"] or (state["ingot"] >= 3 and state["stick"] >= 2)):
                return inf
            if "wooden_axe" in action_name and (state["stone_axe"] or (state["cobble"] >= 3 and state["stick"] >= 2)):
                return inf


    #If we have no ore, don't get coal
    if state["ore"] == 0 and state["coal"] > 0:
        return inf
    #If we have ore, don't get more ore, smelt it instead
    if state["ore"] > 1:
        return inf
    #If we have coal, don't get more coal, use it for smelting:
    if state["coal"] > 1:
        return inf
    #Check to see that if we can smelt ore, we are doing so
    #Essentially if we're doing anything else, don't do it
    if state["ore"] == 1 and "for coal" not in action_name and state["furnace"] and state["coal"] == 1 and "craft furnace" not in action_name:
        return inf

    #If we're smelting, always do this (if we weren't going to smelt we shouldn't have mined)
    if action_name == "smelt ore in furnace":
        return -inf
    #print (action_name + " returned 0")
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    frontQueue = []
    heappush(frontQueue, (0, state))

    came_from = dict()
    cost_so_far = dict()
    action_to_state = dict()

    action_to_state[state] = None
    came_from[state] = None
    cost_so_far[state] = 0

    while frontQueue and time() - start_time < limit:
        _, current_state = heappop(frontQueue)
        #if current_state in action_to_state:
        #    print (action_to_state[current_state])
        #print(current_state)
        #print (_)
        if _ == inf:
            #print (frontQueue[0:100])
            break

    #    if current_state["wooden_pickaxe"] == 1:
    #        if current_state["wooden_axe"] == 0:
    #            print("aha")
    #            print(new_state["cobble"])

    #    if current_state["wooden_axe"] == 0:
        #    if current_state["stone_pickaxe"] == 1:
        #        print("WWWWWWWWWWW")
    #----------------------------------------------------------------
    #is what happens if we find destination
        if is_goal(current_state):
            pathCells = []
            cs = current_state
            while cs is not state:
                action = action_to_state[cs] #action to lead up to previous state
                pathCells.append((cs, action)) #append previous state and the action
                cs = came_from[cs] #go back one, this has to be on the end because otherwise we might be putting in None. I guess I can do while came_from[cs] is not none but too late im sticking with it
            pathCells.reverse()
            return pathCells
    #-----------------------------------------------------------------

        for name, new_state, cost_to_state in graph(current_state):
            cost = cost_to_state
            new_cost = cost_so_far[current_state] + cost
            if new_cost != inf and (new_state not in cost_so_far or new_cost < cost_so_far[new_state]):
                #print("adding")
                cost_so_far[new_state] = new_cost
                priority = new_cost + heuristic(new_state, name)
                if new_state["wooden_pickaxe"] == 1:
                    if new_state["wooden_axe"] == 0:
                        if new_state["cobble"] == 3:
                            print(new_state)
                            print(new_cost)
                            print(priority)
                heappush(frontQueue, (priority, new_state))
                came_from[new_state] = current_state
                action_to_state[new_state] = name
    #            print(new_state)

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
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
        print (len(resulting_plan))
