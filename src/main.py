
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
import harvester
import globals
import builder
import tower
import links
import miner
import tank

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def main():
    """
    Main game logic loop.
    """

   #Clean the memory of dead creeps
    for mem_name in Object.keys(Memory.creeps):
       if not Game.creeps[mem_name]:
           del Memory.creeps[mem_name]

    # Run Towers in all rooms
    for struct in Object.keys(Game.structures):
        s = Game.structures[struct]
        if s.structureType == STRUCTURE_TOWER:
            tower.run_tower(s)

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]

        links.runLinks(spawn)
        
        # Get the number of our creeps in this room.
        creepCount = globals.getMyCreepsInRoom(spawn.pos.roomName)
    
        if not spawn.spawning:
            #We set this to true if we are actually going to spawn a creep
            createSpawn = False
            allRoadHarvesters = True #spawn.room.find(FIND_MY_CREEPS, {"filter": lambda s: ((s.memory.role == "harvester" and s.memory.allRoads == True))}).length == creepCount.num_harvesters and creepCount.num_harvesters != 0
            spawnLink = globals.getSpawnLink(spawn)
            makeMiner = globals.getExtractableMinerals(spawn.room)
            
            #determine if I need to spawn combat creeps. every single spawn will try and create combat creeps during an attack (for now)
            #TODO - also spawn combat creeps if there are hostiles in the current room
            createCombatCreeps = False
            flags = globals.getFlags(globals.FLAG_ATTACK)
            attackFlag = None
            attackRoomName = None
            if flags:
                createCombatCreeps = True
                attackFlag = flags[0]
                attackRoomName = attackFlag.pos.roomName

            #If we have less than the total max of harvesters, create a harvester
            if ((creepCount.num_harvesters < globals.MAX_HARVESTERS[spawn.pos.roomName] and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable) \
                or creepCount.num_harvesters == 0) and spawn.room.energyAvailable >= globals.CREEP_MIN_POWER[spawn.pos.roomName]:
                createHarvesterBuilder = True
                is_harvester = True
                memory = { "memory": { "role": "harvester", "spawnLink": spawnLink } }                
            #otherwise, create a builder
            elif creepCount.num_builders < globals.MAX_BUILDERS[spawn.pos.roomName] and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable and \
                spawn.room.energyAvailable >= globals.CREEP_MIN_POWER[spawn.pos.roomName]:
                createHarvesterBuilder = True
                is_builder = True
                memory = { "memory": { "role": "builder", "spawnLink": spawnLink } }
            
            if createHarvesterBuilder:
                if globals.DEBUG_CREEP_CREATION:
                    print("All road harvesters: " + allRoadHarvesters + " Total harvesters: " + creepCount.num_harvesters)    
                creep_name = Game.time
                if is_harvester:
                    energy = _.min([spawn.room.energyAvailable, globals.HARVESTER_MAX_POWER[spawn.pos.roomName]])
                elif is_builder:
                    energy = _.min([spawn.room.energyAvailable, globals.BUILDER_MAX_POWER[spawn.pos.roomName]])
                creepParts = []
                energyUnits = _(energy / globals.CREEP_MIN_POWER[spawn.pos.roomName]).floor()
                energyRemainder = energy - (energyUnits * globals.CREEP_MIN_POWER[spawn.pos.roomName])
                for part in range(0, energyUnits):
                    #for each energy unit of 300
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)

                #python really needs a switch block
                if energyRemainder == 250:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)                        
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(WORK)                        
                elif energyRemainder == 200:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)
                elif energyRemainder == 150:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                elif energyRemainder == 100:
                    if allRoadHarvesters:
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                elif energyRemainder == 50:
                    if allRoadHarvesters:
                        creepParts.append(CARRY)
                    else:
                        creepParts.append(MOVE)
                createSpawn = True

            elif makeMiner and creepCount.num_miners < 1 and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable and \
                spawn.room.energyAvailable >= globals.CREEP_MIN_POWER[spawn.pos.roomName] and globals.MINE_MINERALS[spawn.pos.roomName]:
                memory = { "memory": { "role": "miner", "mineral": makeMiner } }
                if globals.DEBUG_CREEP_CREATION:
                    print("Creating miner")
                creep_name = Game.time
                energy = _.min([spawn.room.energyAvailable, globals.MINER_MAX_POWER[spawn.pos.roomName]])
                creepParts = []
                energyUnits = _(energy / globals.CREEP_MIN_POWER[spawn.pos.roomName]).floor()
                energyRemainder = energy - (energyUnits * globals.CREEP_MIN_POWER[spawn.pos.roomName])
                for part in range(0, energyUnits):
                    #for each energy unit of 300
                    creepParts.append(MOVE)
                    creepParts.append(WORK)
                    creepParts.append(WORK)
                    creepParts.append(CARRY)
                
                #python really needs a switch block
                if energyRemainder == 250:
                    creepParts.append(WORK)
                    creepParts.append(WORK)
                    creepParts.append(CARRY)                       
                elif energyRemainder == 200:
                    creepParts.append(WORK)
                    creepParts.append(WORK)
                elif energyRemainder == 150:
                    creepParts.append(CARRY)
                    creepParts.append(WORK)
                elif energyRemainder == 100:
                    creepParts.append(WORK)
                elif energyRemainder == 50:
                    creepParts.append(CARRY)
                createSpawn = True

            elif createCombatCreeps and spawn.room.energyAvailable >= globals.COMBAT_CREEP_MIN_POWER[spawn.pos.roomName] \
                and globals.getMyCreepsInRoom(attackRoomName).num_tanks < globals.MAX_TANKS[spawn.pos.roomName]:
                #TODO: Logic to determine what type of combat creep to create, for now just create a tank
                memory = { "memory": { "role": "tank", "spawnId": spawn.id } }
                if globals.DEBUG_CREEP_CREATION:
                    print("Creating tank")
                creep_name = Game.time
                #combat creeps have an exact creation, instead of being scalable (at least for now)
                creepParts = []
                for i in range(0, 10):
                    creepParts.append(TOUGH)
                for i in range(0, 19):
                    creepParts.append(MOVE)
                for i in range(0, 9):
                    creepParts.append(ATTACK)
                createSpawn = True

            if createSpawn:
                result = spawn.spawnCreep(creepParts, creep_name, memory)
                if result != OK:
                    print("Ran into error creating creep: " + result + " with energy " + energy + " with role: " + memory.memory.role + " with parts: " + creepParts)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new creep named " + creep_name + " with energy " + energy + " with role: " + memory.memory.role + " with parts: " + creepParts)
    
    # Run creeps in all rooms
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role == "harvester":
            harvester.run_harvester(creep)
        elif creep.memory.role == "builder":
            builder.run_builder(creep)
        elif creep.memory.role == "miner":
            miner.run_miner(creep)
        elif creep.memory.role == "tank":
            tank.run_tank(creep)



module.exports.loop = main
