import sys
import random

COSTS = {
    "BASIC": [1, 0, 0, 0],
    "HARVESTER": [0, 0, 1, 1],
    "TENTACLE": [0, 1, 1, 0],
    "SPORER": [0, 1, 0, 1],
    "ROOT": [1, 1, 1, 1],
}

organ_types = ["BASIC", "HARVESTER", "TENTACLE", "SPORER", "ROOT"]

protein_types = ["A", "B", "C", "D"]

class Game:
    def __init__(self, width, height):
        self._grid = [[" " for _ in range(width)] for _ in range(height)]
        self._entities = [[Entity() for _ in range(width)] for _ in range(height)]
        self._width = width
        self._height = height
        self.my_organisms = {}
        self.opp_organs = []
        self.protein_entities={'A': [], 'B': [], 'C': [], 'D': []}
        self.organ_map= {}
        self.resources = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

    def update_resources(self, my_a, my_b, my_c, my_d):
        self.resources = {'A': my_a, 'B': my_b, 'C': my_c, 'D': my_d}

    def can_grow(self, organ_type):
        """Checks if there are enough resources for a specific organ type."""
        costs = COSTS.get(organ_type)
        return all(self.resources[res] >= costs[i] for i, res in enumerate("ABCD"))


    def is_valid(self, x, y):
        """Checks if a cell is within bounds and contains a valid entity type for exploration."""
        return (0 <= x < self._width and 0 <= y < self._height and 
                self._entities[y][x].type in ['A', 'B', 'C', 'D', 'Z'])

    def update(self, entity):
        """Updates the grid with the provided entity and initializes organisms if necessary."""
        self._grid[entity.y][entity.x] = entity.type[0]
        self._entities[entity.y][entity.x] = entity

        if entity.type in organ_types:
            self.organ_map[entity.id] = entity
        
        if entity.type in protein_types:
            self.protein_entities[entity.type].append(entity)

        if entity.owner==0:
            self.opp_organs.append(entity)

        # Track my organisms     
        if entity.owner == 1:
            my_organisms.setdefault(entity.organ_root_id, Organism()).update(entity)
            # if entity.organ_root_id not in my_organisms:
            #     my_organisms[entity.organ_root_id] = Organism()
            # else:
            #     my_organisms[entity.organ_root_id].update(entity)

    def get_explorable(self, entity):
        """Finds neighboring cells that can be explored or grown into."""
        candidates = []
        x, y = entity.x, entity.y
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                candidates.append((nx, ny, self._entities[ny][nx].type, entity))
        
        return candidates

    def get_basic(self, organism):
        """Determines the best growth action for the organism based on explorable neighbors."""
        candidates = []
        success = True
        for organ in organism.organs:
            candidates += self.get_explorable(organ)

        #candidates.sort(key=lambda x: x[2])  # Sort by type for priority

        if candidates:
            target_x, target_y, _, parent = random.choice(candidates) #candidates[0]
            return success,target_x, target_y, parent
        else:
            return False,-1,-1,None

    def closest_target(self,start_entities,target_entities):
        min_distance = 1000
        max_distance = 0
        start_organ = None
        target=None
        for organ in start_entities:
            #debug("organ:",organ )
            for target_entity in target_entities:
                distance = organ.distance(target_entity)
                if distance < min_distance:
                    min_distance = distance
                    target = target_entity
                    start_organ = organ
                if distance > max_distance:
                    max_distance = distance
        #debug(min_distance)
        return start_organ,target,min_distance,max_distance
        

    def closest_intermediate_target(self,start_organ,target):
        x_distance =start_organ.x-target.x
        y_distance =start_organ.y-target.y
        new_target_x, new_target_y = start_organ.x, start_organ.y
        if min(abs(x_distance),abs(y_distance))== abs(y_distance):
            if y_distance >0:
                new_target.y = new_target.y-1
            elif y_distance <0:
                new_target.y = new_target.y+1
        else:
            if x_distance >0:
                new_target.x = new_target.x-1
            elif x_distance <0:
                new_target.x = new_target.x+1
        return self._entities[new_target_y][new_target_x]

    def get_action(self, organism):
        # try ROOT creation
        if organism.sporers and self.can_grow("ROOT"):
            # organism has sporers and there are enough resources to spore a new ROOT
            # get closest target to organism sporers   
            start_organ,target,min_distance,max_distance= self.closest_target(organism.sporers,self.protein_entities["A"])
            # target is on the same line
            if start_organ.on_the_same_line(target): 
                return f"SPORE {start_organ.id} {target.x} {target.y}"

        cell_type = "BASIC"
        # get closest target A Protein to organism organs (that are not sporers) 
        start_organ,target,min_distance,max_distance= self.closest_target(organism.organs,self.protein_entities["A"])

        # try SPORER creation
        if min_distance > self.resources['A']:
            # target is far (not enough resources)
            intermediate_target = self.closest_intermediate_target(start_organ,target)
            direction  = intermediate_target.direction(target)
            # grow sporer if possible
            if intermediate_target.on_the_same_line(target):
                if self.can_grow("SPORER"):
                    cell_type = "SPORER"                
            return  f"GROW {start_organ.id} {intermediate_target.x} {intermediate_target.y} {cell_type} {direction}"

        # get closest Enemy target to organism organs (that are not sporers) 
        start_organ_to_enemy,enemy_target,min_distance_to_enemy,max_distance_to_enemy= self.closest_target(organism.organs,self.opp_organs)
        
        # try TENTACLE creation
        if min_distance_to_enemy == 2 and start_organ_to_enemy.on_the_same_line(enemy_target) and self.can_grow("TENTACLE"):
            direction =  start_organ_to_enemy.direction(enemy_target)
            cell_type="TENTACLE"
            return f"GROW {start_organ_to_enemy.id} {enemy_target.x} {enemy_target.y} {cell_type} {direction}"

        # try HARVESTER creation
        if min_distance == 2 and start_organ.on_the_same_line(target) and self.can_grow("HARVESTER"):
            direction =  start_organ.direction(target)
            cell_type="HARVESTER"
            return f"GROW {start_organ.id} {target.x} {target.y} {cell_type} {direction}"

        if min_distance == 1:
            direction =  start_organ.direction(target)
            return f"GROW {start_organ.id} {target.x} {target.y} {cell_type} {direction}"
        
        # try BASIC creation
        if max_distance <=2:
            success,targetx, targety, start_organ = self.get_basic(organism)
            if success:
                return  f"GROW {start_organ.id} {targetx} {targety} {cell_type}"
            else:
                return "WAIT"

        action_basic = f"GROW {start_organ.id} {target.x} {target.y} {cell_type}"
        return action_basic
            
class Organism:
    def __init__(self):
        self.root = None
        self.organs = []
        self.organ_ids = []
        self.sporers = []

    def update(self, entity):
        """Adds an entity to the organism if not already present."""
        if entity.type == "ROOT"
            self.root = entity
        if entity.id not in self.organ_ids:
            if entity.type == "SPORER":
                self.sporers.append(entity) 
            else:
                self.organs.append(entity)
            self.organ_ids.append(entity.id)
            

class Entity:
    def __init__(x=-1, y=-1, entity_type="Z", owner=-1, organ_id=-1, organ_dir="D", organ_parent_id=-1, organ_root_id=-1):
        self.x = x
        self.y = y
        self.type = entity_type
        self.owner = owner
        self.id = organ_id
        self.organ_dir = organ_dir
        self.organ_parent_id = organ_parent_id
        self.organ_root_id = organ_root_id

    def __str__(self):
        return f"{self.x},{self.y},{self.id},{self.type},{self.owner},{self.organ_parent_id},{self.organ_root_id}"

    def distance(self,e2):
        return abs(self.x-e2.x)+abs(self.y -e2.y)

    def on_the_same_line(self,e):
        return self.x == e.x or self.y == e.y
    
    def direction(self,e):
        if self.x == e.x:
            if self.y > e.y:
                return "N"
            else:
                return "S"
        if self.y == e.y:
            if self.x > e.x:
                return "W"
            else:
                return "E"
        return self.organ_dir

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

# Initialization
width, height = map(int, input().split())

# Main game loop
while True:
    entity_count = int(input())
    game = Game(width, height)

    for _ in range(entity_count):
        inputs = input().split()
        x, y = int(inputs[0]), int(inputs[1])
        entity_type = inputs[2]
        owner = int(inputs[3])
        organ_id = int(inputs[4])
        organ_dir = inputs[5]  # Not currently used
        organ_parent_id = int(inputs[6])
        organ_root_id = int(inputs[7])

        entity = Entity(x, y, entity_type, owner, organ_id, organ_dir, organ_parent_id, organ_root_id)
        game.update(entity)


    # Player's resources
    my_a, my_b, my_c, my_d = map(int, input().split())
    game.update_resources(my_a, my_b, my_c, my_d)
    opp_a, opp_b, opp_c, opp_d = map(int, input().split())
    required_actions_count = int(input())

    for i in range(required_actions_count):
        organism = game.my_organisms[i]
        result = game.get_action(organism)

        if result:
            print(result)
            #print(f"GROW {parent.id} {target_x} {target_y} BASIC")
