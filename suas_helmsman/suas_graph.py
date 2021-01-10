import itertools
from math import pi, sqrt, tan
from typing import List, Optional, Tuple
import networkx as nx
from pygeodesy.ecef import EcefCartesian
from shapely.geometry import LinearRing, LineString, Point, Polygon

from suas_helmsman.data import Obstacle, Waypoint


class SUASGraph:
    """An SUASGraph is an object conatining all the nessecary data to generate a flight path for SUAS.

    This is done by constructing a networkx graph, adding all points of interest, then creating an edge graph.
    All actual graph construction is deligated to the functions.
    This graph is generated in cartesian coordinates with (0, 0) being the lost coms point with all distances being feet.
    """

    def __init__(self, starting_point, alt_bounds) -> None:
        """Constructs a SUASGraph.

        Args:
            starting_point (Dictionary): A starting point within the bounds
            alt_bounds (Dictionary): the altitude bounds
        """
        self.starting_point = starting_point
        # Cartesian Coordiates System centered at lost coms point
        self.cartesian = EcefCartesian(
            starting_point["latitude"], starting_point["longitude"]
        )
        # Construct Graph and add initial point
        self.graph = nx.empty_graph(0)
        # self.graph.add_node((0, 0, 200))
        # POIs
        self.alt_bounds = alt_bounds
        self.waypoints: List[Waypoint] = []
        self.obstacles: List[Obstacle] = []
        self.boundaries: List[Point] = []
        self.boundary_ring: LinearRing = None
        self.boundary_poly: Polygon = None
        self.drop: Optional[Point] = None
        self.off_axis: Optional[Point] = None
        self.off_axis_optimal: Optional[Point] = None
        self.path: List[Tuple] = []

    def add_boundaries(self, bounds) -> None:
        """Adds the flight boundary points to the graph.

        Args:
            bounds (Dictionary): Dictionary of lat lon points
        """
        for b in bounds:
            # Convert each bound to xy coordinate
            # Forward converts from latlon to cartesian
            x, y, *_ = self.cartesian.forward(b["latitude"], b["longitude"])

            # Add buffer to bounds
            x += 5 * (-1 if b["latitude"] > self.starting_point["latitude"] else 1)
            y += 5 * (-1 if b["longitude"] > self.starting_point["longitude"] else 1)

            # Add to list
            self.boundaries.append(Point(x, y))
        self.boundary_ring = LinearRing(self.boundaries)
        self.boundary_poly = Polygon(self.boundaries)

    def add_waypoints(self, way) -> None:
        """Adds the waypoints to the graph.

        Args:
            way (Dictionary): Dictionary of lat lon points
        """
        for (i, w) in enumerate(way):
            # Convert each bound to xy coordinate
            # Forward converts from latlon to cartesian
            x, y, *_ = self.cartesian.forward(w["latitude"], w["longitude"])

            # Add to internal list and graph
            self.waypoints.append(Waypoint(Point(x, y, w["altitude"]), i))
            self.graph.add_node((x, y, w["altitude"]))

    def add_obstacles(self, obs) -> None:
        """Adds obstacles to graph.

        Args:
            obs (Dictionary): Dictionary of lat lon points
        """
        for o in obs:
            # Convert each bound to xy coordinate
            # Forward converts from latlon to cartesian
            x, y, *_ = self.cartesian.forward(o["latitude"], o["longitude"])

            # Add each point to the list and the graph
            obi = Obstacle(Point(x, y, self.alt_bounds[0]), o["radius"], o["height"])
            self.obstacles.append(obi)
            for n in obi.points():
                p = Point(*n)
                if self.boundary_poly.contains(p):
                    self.graph.add_node(n)

    def add_off_axis(self, off) -> None:
        """Adds the off axis point to the graph and generates an optimal point

        Args:
            off (Dictionary): Dictionary of lat lon points
        """
        # Convert each bound to xy coordinate
        # Forward converts from latlon to cartesian
        x, y, *_ = self.cartesian.forward(off["latitude"], off["longitude"])
        point = Point(x, y, 0)

        # Find the optimal off axis point by interpolating the point onto the ring
        off_point = self.boundary_ring.interpolate(self.boundary_ring.project(point))
        # Calculate the height of the point
        dis = off_point.distance(point)
        z = min(dis * tan(75 * pi / 180), 325)
        # Add optimal point to graph
        self.off_axis_optimal = Point(off_point.x, off_point.y, z)
        self.graph.add_node(
            (self.off_axis_optimal.x, self.off_axis_optimal.y, self.off_axis_optimal.z)
        )
        # Add actual off axis point
        self.off_axis = point

    def add_drop(self, drop) -> None:
        """Adds the optimal drop point to the graph

        Args:
            drop (Dictionary): Dictionary of lat lon points
        """
        # Convert each bound to xy coordinate
        # Forward converts from latlon to cartesian
        x, y, *_ = self.cartesian.forward(drop["latitude"], drop["longitude"])
        # Add point to graph
        self.drop = Point(x, y, 500)
        self.graph.add_node((self.drop.x, self.drop.y, self.drop.z))

    def add_edges(self) -> None:
        """Constructs all possible fly paths for the plane.

        This checks every combination of points to see if they are valid to fly.
        A path is valid if it does not pass through an obstacle and has less than a 15% incline
        """
        print(self.graph.number_of_nodes())
        counter = 0
        for node, other in itertools.product(self.graph, self.graph):
            # Check to see if graph already has edge
            if node is other or self.graph.has_edge(node, other):
                continue
            # Calculate slopes
            slopexz = (
                abs((other[2] - node[2]) / (other[0] - node[0]))
                if other[0] - node[0] != 0
                else 2
            )
            slopeyz = (
                abs((other[2] - node[2]) / (other[1] - node[1]))
                if other[1] - node[1] != 0
                else 2
            )
            if slopexz >= 0.9 and slopeyz >= 0.9:
                continue
            # Add edges to graph
            seg = LineString([node, other])
            if len(self.obstacles) == 0:
                # If there are no edges then all edges
                self.graph.add_edge(node, other, weight=seg.length)
            # Compare each potential path to obstacles to see if valid
            inter = not self.boundary_ring.intersection(seg).is_empty
            for o in self.obstacles:
                if inter or solve_intersection(o, seg):
                    inter = True
                    break
            if not inter:
                self.graph.add_edge(node, other, weight=seg.length)
            counter += 1  #
            if counter % 10000 == 0:
                print(counter)
        print(len(self.graph.edges()))

    def construct_path(self) -> None:
        """Constructs the flight path using the A* Algorithm.
        This is done in this order:
        1. Construct path of just waypoints
        2. Check to see if it is possible to do offaxis and drop while flying path
        3. If not generate most optimal after
        """
        off_check = self.off_axis == None
        drop_check = self.drop == None
        path = []
        # Generate waypoints
        for i in range(len(self.waypoints) - 1):
            seg = []
            seg.extend(
                nx.astar_path(
                    self.graph,
                    *self.waypoints[i].point.coords,
                    *self.waypoints[i + 1].point.coords,
                    heuristic
                )
            )
            print(i, seg, self.graph.has_edge(seg[0], seg[len(seg) - 1]))

            if i == 0:
                path.extend(seg)
            else:
                path.extend(seg[1:])
        # Check path to see if passes through offaxis/drop
        ring = LineString(path)
        if self.off_axis != None:
            off_point = ring.interpolate(ring.project(self.off_axis))
            off_dis = off_point.distance(self.off_axis)
            if off_point.z / off_dis > 2.74:
                off_check = True
                self.off_axis_optimal = off_point
        if self.drop != None:
            drop_point = ring.interpolate(ring.project(self.drop))
            drop_dis = drop_point.distance(self.drop)
            if drop_dis < 15:
                drop_check = True
                self.drop = drop_point
        seg = []
        # Generate remaining POIs
        if not off_check and not drop_check:
            off_drop_dis = nx.astar_path_length(
                self.graph,
                path[len(path) - 1],
                *self.off_axis_optimal.coords,
                heuristic
            )
            drop_off_dis = nx.astar_path_length(
                self.graph, path[len(path) - 1], *self.drop.coords, heuristic
            )
            if off_drop_dis < drop_off_dis:
                seg.extend(
                    nx.astar_path(
                        self.graph,
                        path[len(path) - 1],
                        *self.off_axis_optimal.coords,
                        heuristic
                    )[1:]
                )
                seg.extend(
                    nx.astar_path(
                        self.graph,
                        *self.off_axis_optimal.coords,
                        *self.drop.coords,
                        heuristic
                    )[1:]
                )
            else:
                seg.extend(
                    nx.astar_path(
                        self.graph, path[len(path) - 1], *self.drop.coords, heuristic
                    )[1:]
                )
                seg.extend(
                    nx.astar_path(
                        self.graph,
                        *self.drop.coords,
                        *self.off_axis_optimal.coords,
                        heuristic
                    )[1:]
                )
        elif not off_check:
            seg.extend(
                nx.astar_path(
                    self.graph,
                    path[len(path) - 1],
                    *self.off_axis_optimal.coords,
                    heuristic
                )[1:]
            )
        elif not drop_check:
            seg.extend(
                nx.astar_path(
                    self.graph, path[len(path) - 1], *self.drop.coords, heuristic
                )[1:]
            )
        path.extend(seg)
        self.path = path

    def path_lat_lon_alt(self) -> List[Tuple[float, float, float]]:
        """Returns the path in lat long alt coordinates

        Returns:
            List[Tuple]: List of Tuples as (lat, long, alt)
        """
        temp = []
        for x, y, z in self.path:
            # Reverse converts from (x,y) to (lat, lon)
            _, _, _, lat, lon, *_ = self.cartesian.reverse(x, y, 0)
            temp.append((lat, lon, z))
        return temp


def heuristic(node, end_node) -> float:
    """Heuristic Function used in Networkx as H score

    Measures the distance from the end point

    Args:
        node (Tuple): Initial Point
        end_node (Tuple): Final Point

    Returns:
        float: H score
    """
    # Cost for doing different actions, used to calculate G and H scores
    # Distance of going straight
    straight_cost = 1
    # Distance of going diagonal on a square, estimate of sqrt(2)
    first_diag_cost = sqrt(2)
    # Distance of going diagonal on a cube, estimate of sqrt(3)
    sec_diag_cost = sqrt(3)

    dx = abs(node[0] - end_node[0])
    dy = abs(node[1] - end_node[1])
    dz = abs(node[2] - end_node[2])
    dmin = min(dx, dy, dz)
    dmax = max(dx, dy, dz)
    dmid = dx + dy + dz - dmin - dmax
    return (
        (sec_diag_cost - first_diag_cost) * dmin
        + (first_diag_cost - straight_cost) * dmid
        + dmax * first_diag_cost
    )


def solve_intersection(o: Obstacle, seg: LineString) -> bool:
    """Solves the intersection between an obstacle and a LineString

    Args:
        o (Obstacle): The Obstacle to compare against
        seg (LineString): The potential flight path to compare against

    Returns:
        Bool: False if no intersection, True otherwise
    """
    inters = o.shapely.intersection(seg)
    return not inters.is_empty
