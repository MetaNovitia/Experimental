# Gunfire Reborn Rune Stone Optimizer

import time

# name, points (x, y, value)
# x represents column, y represents row.
PIECE_MAP = {
    "A": [(2, 0, 4), (0, 2, 4)],
    "B": [(-2, 2, 4)],
    "C": [(2, 2, 3)],
    "D": [(-1, 1, 4)],
    "E": [(1, -1, 2), (-2, 0, 2), (-1, 0, 3), (-1, 1, 2), (0, 1, 2), (0, 2, 4)],
    "F": [(0, -2, 2), (2, -2, 1)],
    "G": [(0, -2, 2), (0, -1, 4), (1, 0, 2)],
    "H": [(0, -1, 3), (-1, 0, 1)],
}

PIECES = [key for key in PIECE_MAP]

BADGES = sorted([10, 10, 8, 8, 8, 6, 6, 6], reverse=True)
MAX_POINTS = sum(BADGES)
THRESHOLD = min(54, MAX_POINTS)
MAX_LOST_POINTS = 1

POINT_MOD = 2

ROWS = 4
COLS = 4


class Point:
  """Immutable point on a 2D grid."""

  def __init__(self, x: int, y: int, value: int):
    self.x = x
    self.y = y
    self.value = value

  def rotate(self, num_rotations: int):
    """Rotates the piece 90 degrees clockwise."""
    new_x, new_y = self.x, self.y
    for _ in range(num_rotations):
      new_x, new_y = -new_y, new_x
    return Point(new_x, new_y, self.value)

  def displace(self, dx: int, dy: int):
    """Displaces the point by the given amount."""
    return Point(self.x + dx, self.y + dy, self.value)


class Piece:
  """Immutable rune energy piece."""

  def __init__(self, name: str, points: list[Point]):
    self.name = name
    self.points = points

  def get_points(self, x: int, y: int, num_rotations: int):
    """Returns the points for the given index."""
    return [p.rotate(num_rotations).displace(x, y) for p in self.points]


class Graph:
  """Graph."""

  def __init__(self, badges: list[int] | None = None):
    self.graph = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    self.badges = sorted(badges, reverse=True) if badges else []
    self.score = -1
    self.lost_points = 0

  def is_valid(self, x: int, y: int):
    return x >= 0 and x < COLS and y >= 0 and y < ROWS

  def is_empty(self, x: int, y: int):
    return isinstance(self.graph[y][x], int)

  def insert(self, x: int, y: int, num_rotations: int, piece: Piece):
    """Inserts value into self.m."""
    self.score = -1

    if not self.is_empty(x, y):
      print("Error: overlap")
      return False

    if self.graph[y][x] > 0:
      self.lost_points += self.graph[y][x]
      if self.lost_points > MAX_LOST_POINTS:
        return False
    self.graph[y][x] = piece.name + str(num_rotations)

    points = piece.get_points(x, y, num_rotations)
    for p in points:
      if self.is_valid(p.x, p.y) and self.is_empty(p.x, p.y):
        self.graph[p.y][p.x] += p.value
      else:
        self.lost_points += p.value
        if self.lost_points > MAX_LOST_POINTS:
          return False

    return True

  def get_score(self):
    """Returns the score of the graph."""
    if self.score >= 0:
      return self.score

    points = []
    for row in self.graph:
      for val in row:
        if isinstance(val, int) and val > 0:
          points.append(val)
    sorted_points = sorted(points, reverse=True)
    score = 0
    for i in range(min(len(self.badges), len(sorted_points))):
      score += min(sorted_points[i] // POINT_MOD * POINT_MOD, self.badges[i])
    return score

  def copy(self):
    res = Graph()
    res.graph = [row[:] for row in self.graph]
    res.badges = self.badges[:]
    return res

  def __repr__(self):
    space = 0
    for row in self.graph:
      for val in row:
        if isinstance(val, str):
          space = max(space, len(val))
        else:
          space = max(space, len(str(val)))

    res = ""
    for y in range(ROWS):
      for x in range(COLS):
        val = self.graph[y][x]
        res += str(val).center(space) + " "
      res += "\n"
    res += "score: " + str(self.get_score())
    return res

  def __lt__(self, other):
    return self.get_score() < other.get_score()

  def __gt__(self, other):
    return self.get_score() > other.get_score()


def recurse(graph: Graph, remaining_pieces: list[Piece]):
  """Recurse."""
  if not remaining_pieces:
    return graph

  result_graphs = []
  piece = remaining_pieces[0]
  for y in range(ROWS):
    for x in range(COLS):
      if not graph.is_empty(x, y):
        continue

      # Try all rotations.
      for num_rotations in range(4):
        new_graph = graph.copy()
        success = new_graph.insert(x, y, num_rotations, piece)
        if success:
          result = recurse(new_graph, remaining_pieces[1:])
          if result:
            if result.get_score() >= THRESHOLD:
              return result
            result_graphs.append(result)

  if not result_graphs:
    return None
  return max(result_graphs)


if __name__ == "__main__":
  time_start = time.time()
  print(
      recurse(
          Graph(BADGES),
          [
              Piece(name, [Point(x, y, v) for x, y, v in PIECE_MAP[name]])
              for name in PIECES
          ],
      )
  )
  time_end = time.time()
  print("time: ", time_end - time_start)
