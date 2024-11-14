import sys
import random

COSTS={"BASIC":[1,0,0,0],
"HARVESTER":[0,0,1,1],
"TENTACLE":[0,1,1,0],
"SPORER":[0,1,0,1],
"ROOT":[1,1,1,1],
}
class Game:
    def __init__(self, width, height):
        self._grid = [[" " for _ in range(width)] for _ in range(height)]
        self._entities = [[Entity() for _ in range(width)] for _ in range(height)]
        self._width = width
        self._height = height
        self.our_organs = []
        self.my_organisms = []
        self.first_round = True
        self.A_Entities=[]
        self.Opp_Entities = []
        self.resources=[]

    def sporer_is_possible(self):
        if self.resources[1]>0 and self.resources[3]>0:
            return True

    def is_valid(self, x, y):
        """Checks if a cell is within bounds and contains a valid entity type for exploration."""
        return (0 <= x < self._width and 0 <= y < self._height and 
                self._entities[y][x].type in ['A', 'B', 'C', 'D', 'Z'])

    def update(self, entity):
        """Updates the grid with the provided entity and initializes organisms if necessary."""
        self._grid[entity.y][entity.x] = entity.type[0]
        self._entities[entity.y][entity.x] = entity
        
        if entity.type=="A" :
            self.A_Entities.append(entity)

        if entity.owner==0:
            self.Opp_Entities.append(entity)

        # Track player's organisms and roots
        if entity.owner == 1:
            if entity.type == "ROOT" and self.first_round:
                organism = Organism(entity)
                organism._organ_ids.append(entity.id)
                self.my_organisms.append(organism)
            elif entity.id not in self.my_organisms[-1]._organ_ids:
                self.my_organisms[-1].graph.append(entity)
                self.my_organisms[-1]._organ_ids.append(entity.id)

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

    def get_actionV2(self, organism):
        """Determines the best growth action for the organism based on explorable neighbors."""
        candidates = []
        for organ in organism.graph:
            candidates += self.get_explorable(organ)

        candidates.sort(key=lambda x: x[2])  # Sort by type for priority
        min_distance = 1000
        start_organ = None
        target=None
        for e in game.A_Entities:
            #debug("Entity A:",e, organism.root.distance(e) )
            for candidate[3] in candidates:
                if candidate.distance(e) < min_distance:
                    min_distance = candidate.distance(e)
                    target = e
                    start_organ = candidate

        if candidates:
            target_x, target_y, _, parent = target.x, target.y, _,start_organ
            return target_x, target_y, parent
        return None

    def get_basic(self, organism):
        """Determines the best growth action for the organism based on explorable neighbors."""
        candidates = []
        success = True
        for organ in organism.graph:
            candidates += self.get_explorable(organ)

        #candidates.sort(key=lambda x: x[2])  # Sort by type for priority

        if candidates:
            target_x, target_y, _, parent = random.choice(candidates) #candidates[0]
            return success,target_x, target_y, parent
        else:
            return False,-1,-1,None

    def closer_interest(self,organism,adverse_entities):
        min_distance = 1000
        start_organ = None
        target=None
        for organ in organism.graph:
            #debug("organ:",organ )
            for adversary in adverse_entities:
                my_distance =organ.distance(adversary)
                if my_distance < min_distance:
                    min_distance =  my_distance
                    target = adversary
                    start_organ = organ
        debug(min_distance)
        return start_organ,target,min_distance
        
    def get_actionV3(self, organism):

        # Fetch A entitites
        start_organ,target,min_distance= self.closer_interest(organism,self.A_Entities)
        cell_type = "BASIC"
        
        if min_distance == 1:
            direction =  start_organ.direction(target)
            cell_type="HARVESTER"
            action_harvester = f"GROW {start_organ.id} {target.x} {target.y} {cell_type} {direction}"
            return action_harvester
        else:
            if min_distance <2:
                success,targetx, targety, start_organ = game.get_basic(organism)
                if success:
                    return  f"GROW {start_organ.id} {targetx} {targety} {cell_type}"
                else:
                    return "WAIT"
            action_basic = f"GROW {start_organ.id} {target.x} {target.y} {cell_type}"
            return action_basic

    def get_actionV4(self, organism):

        start_organ,target,min_distance= self.closer_interest(organism,self.Opp_Entities)
        cell_type = "BASIC"
        
        if min_distance == 2:
            direction =  start_organ.direction(target)
            cell_type="TENTACLE"
            action_harvester = f"GROW {start_organ.id} {target.x} {target.y} {cell_type} {direction}"
            return action_harvester
        else:
            if min_distance <2:
                success,targetx, targety, start_organ = game.get_basic(organism)
                if success:
                    return  f"GROW {start_organ.id} {targetx} {targety} {cell_type}"
                else:
                    return "WAIT"
            action_basic = f"GROW {start_organ.id} {target.x} {target.y} {cell_type}"
            return action_basic

    def closest_target_to_A(self,start_organ,target):
        x_distance =start_organ.x-target.x
        y_distance =start_organ.y-target.y
        new_target = start_organ
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
        return new_target

    def get_action(self, organism):
        if self.A_Entities:
            pass
        start_organ,target,min_distance= self.closer_interest(organism,self.A_Entities)
        cell_type = "BASIC"
        if self.sporer_is_possible():
            new_target = self.closest_target_to_A(start_organ,target)
            direction  = new_target.direction(target)
            debug("SPORE",new_target)
            return f"GROW {start_organ.id} {new_target.x} {new_target.y} SPORER {direction}"

        if start_organ.x == new_target.x or start_organ.y == new_target.y: 
            return f"SPORE {start_organ.id} {target.x} {target.y}"
        if min_distance == 2:
            direction =  start_organ.direction(target)
            cell_type="TENTACLE"
            action_harvester = f"GROW {start_organ.id} {target.x} {target.y} {cell_type} {direction}"
            return action_harvester
        else:
            if min_distance <2:
                success,targetx, targety, start_organ = game.get_basic(organism)
                if success:
                    return  f"GROW {start_organ.id} {targetx} {targety} {cell_type}"
                else:
                    return "WAIT"
            action_basic = f"GROW {start_organ.id} {target.x} {target.y} {cell_type}"
            return action_basic
            
class Organism:
    def __init__(self, root):
        self.root = root
        self.graph = [root]
        self._organ_ids = []
        self.closer_A_entities = []

    def update(self, entity):
        """Adds an entity to the organism if not already present."""
        if entity.id not in self._organ_ids:
            self.graph.append(entity)
            self._organ_ids.append(entity.id)

class Entity:
    def __init__(self, organ_id=-1, entity_type="Z", x=-1, y=-1, owner=-1, organ_parent_id=-1, organ_root_id=-1):
        self.id = organ_id
        self.type = entity_type
        self.x = x
        self.y = y
        self.owner = owner
        self.organ_parent_id = organ_parent_id
        self.organ_root_id = organ_root_id

    def __str__(self):
        return f"{self.x},{self.y},{self.id},{self.type},{self.owner},{self.organ_parent_id},{self.organ_root_id}"

    def distance(self,e2):
        return abs(self.x-e2.x)+abs(self.y -e2.y)
    
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

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

# Initialization
width, height = map(int, input().split())
game = Game(width, height)

# Main game loop
while True:
    entity_count = int(input())
    for _ in range(entity_count):
        inputs = input().split()
        x, y = int(inputs[0]), int(inputs[1])
        entity_type = inputs[2]
        owner = int(inputs[3])
        organ_id = int(inputs[4])
        organ_dir = inputs[5]  # Not currently used
        organ_parent_id = int(inputs[6])
        organ_root_id = int(inputs[7])

        entity = Entity(organ_id, entity_type, x, y, owner, organ_parent_id, organ_root_id)
        game.update(entity)


    game.first_round = False

    # Player's resources
    my_a, my_b, my_c, my_d = map(int, input().split())
    game.resources=  [my_a, my_b, my_c, my_d]
    opp_a, opp_b, opp_c, opp_d = map(int, input().split())
    required_actions_count = int(input())

    for i in range(required_actions_count):
        organism = game.my_organisms[i]
        result = game.get_action(organism)
        min_distance=1000

        if result:
            print(result)
            #print(f"GROW {parent.id} {target_x} {target_y} BASIC")
