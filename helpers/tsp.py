"""Simple Travelling Salesperson Problem (TSP) between cities."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from .sheets import import_sheets, export_sheets


def create_data_model():
    """Stores the data for the problem."""
    data = import_sheets()
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""

    ## Print Objective value
    print(f'Objective: {solution.ObjectiveValue()}')

    ## Initialize distance and load counters for all routes
    total_distance = 0
    total_load = 0

    ## For each vehicle...
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Seating for Table {}:\n'.format(vehicle_id)

        ## Route distance and load counters
        route_distance = 0
        route_load = 0

        ## While route is not ended...
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {} -> '.format(data["indices"][node_index])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        ## Add last stop
        plan_output += ' {}\n'.format(data["indices"][manager.IndexToNode(index)])
        ## Add distance to output
        #plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        
        ## Add this route's distances and loads to totals
        total_distance += route_distance
        total_load += route_load

    ## Summary print-out
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))



def save_solution(data, manager, routing, solution):
    
    ## Initialize all_routes list of lists
    all_routes = []

    ## For each vehicle...
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []

        ## While route is not ended...
        while not routing.IsEnd(index):
            ## Extract route starting index
            node_index = manager.IndexToNode(index)

            # If indices is not "depot", add to route output
            if data["indices"][node_index] != "Depot":
                route.append(data["indices"][node_index])
            index = solution.Value(routing.NextVar(index))

        ## Append route list to results        
        all_routes.append(route)

    export_sheets(all_routes)



def tsp():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        #print_solution(data, manager, routing, solution)
        save_solution(data, manager, routing, solution)
    else:
        print('No solution found !')

if __name__ == '__main__':
    tsp()