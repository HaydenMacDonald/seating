"""Simple Travelling Salesperson Problem (TSP) between cities."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from .sheets import sheets


def create_data_model():
    """Stores the data for the problem."""
    data = sheets()
    return data

def print_solution2(data, manager, routing, solution, indices_labels):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        total_distance += route_distance
    print('Total Distance of all routes: {}m'.format(total_distance))

def print_solution(manager, routing, solution, indices_labels):
    """Prints solution on console."""
    print('Objective value: {}'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Wedding Seating Arrangement:\n'
    route_distance = 0
    print_counter = 0
    while not routing.IsEnd(index):
        if print_counter == 7:
            plan_output += ' {}({})\n'.format(indices_labels[manager.IndexToNode(index)], manager.IndexToNode(index))
            print_counter = 0
        else:
            plan_output += ' {}({}) ->'.format(indices_labels[manager.IndexToNode(index)], manager.IndexToNode(index))
            print_counter += 1

        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(indices_labels[manager.IndexToNode(index)])
    print(plan_output)
    plan_output += 'Route distance: {} miles\n'.format(route_distance)


def tsp():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # # Add Distance constraint.
    # dimension_name = 'Distance'
    # routing.AddDimension(
    #     transit_callback_index,
    #     0,  # no slack
    #     3000,  # vehicle maximum travel distance
    #     True,  # start cumul to zero
    #     dimension_name)
    # distance_dimension = routing.GetDimensionOrDie(dimension_name)
    # distance_dimension.SetGlobalSpanCostCoefficient(100)

    # # Define Transportation Requests.
    # for request in data['pickups_deliveries']:
    #     pickup_index = manager.NodeToIndex(request[0])
    #     delivery_index = manager.NodeToIndex(request[1])
    #     routing.AddPickupAndDelivery(pickup_index, delivery_index)
    #     routing.solver().Add(
    #         routing.VehicleVar(pickup_index) == routing.VehicleVar(
    #             delivery_index))
    #     routing.solver().Add(
    #         distance_dimension.CumulVar(pickup_index) <=
    #         distance_dimension.CumulVar(delivery_index))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(manager, routing, solution, data["indices"])



if __name__ == '__main__':
    tsp()