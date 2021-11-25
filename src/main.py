
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
import harvester
import globals
import builder

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

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]

        #create radial construction sites
        """        
        Game.creeps["33493059"].room.getTerrain().get(Game.spawns["Spawn1"].pos.x, Game.spawns["Spawn1"].pos.y)
        0
        Game.creeps["33493059"].room.getTerrain().get(Game.spawns["Spawn1"].pos.x, Game.spawns["Spawn1"].pos.y-2)
        1
        """
        #TODO: Make the radial depth based on the room controller level
        radial_depth = 1
        x_shift = -5
        for i in range(radial_depth):
            for j in range(radial_depth):
                spawn.room.createConstructionSite(spawn.pos.x + i + x_shift, spawn.pos.y + j, STRUCTURE_EXTENSION)
                spawn.room.createConstructionSite(spawn.pos.x - i + x_shift, spawn.pos.y - j, STRUCTURE_EXTENSION)
                spawn.room.createConstructionSite(spawn.pos.x + i + x_shift, spawn.pos.y - j, STRUCTURE_EXTENSION)
                spawn.room.createConstructionSite(spawn.pos.x - i + x_shift, spawn.pos.y + j, STRUCTURE_EXTENSION)

        if not spawn.spawning:
            # Get the number of our creeps in this room.
            num_creeps = 0
            num_harvesters = 0
            num_builders = 0
            for name in Object.keys(Game.creeps):
                creep = Game.creeps[name]
                if creep.pos.roomName == spawn.pos.roomName:
                    if creep.memory.role == "harvester":
                        num_harvesters += 1
                    elif creep.memory.role == "builder":
                        num_builders += 1

            num_creeps = num_harvesters + num_builders
            #if globals.DEBUG_CREEP_CREATION:
            #    print("There are currently " + num_harvesters + " harvesters and " + num_builders + " builders")

            #If we have less than the total max of harvesters, create some harvesters
            if num_harvesters < globals.MAX_HARVESTERS and spawn.room.energyAvailable >= 800:
                #create a super harvester
                creep_name = Game.time
                result = spawn.spawnCreep([MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, WORK, WORK, WORK, WORK, CARRY, CARRY], creep_name, { "memory": { "role": "harvester"} })
                if result != OK:
                    print("Ran into error creating super creep: " + result)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new super harvester named " + creep_name)
            #Same thing, if we have less than the total number of builders make some builders
            if num_builders < globals.MAX_BUILDERS and spawn.room.energyAvailable >= 800:
                #create a super builder
                creep_name = Game.time
                result = spawn.spawnCreep([MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, WORK, WORK, WORK, WORK, CARRY, CARRY], creep_name, { "memory": { "role": "builder"} })
                if result != OK:
                    print("Ran into error creating super creep: " + result)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new super builder named " + creep_name)

            """
            elif num_harvesters < globals.MAX_HARVESTERS and spawn.store.getUsedCapacity(RESOURCE_ENERGY) >= 250:            
                creep_name = Game.time
                result = spawn.spawnCreep([WORK, CARRY, MOVE, MOVE], creep_name, { "memory": { "role": "harvester"} })
                if result != OK:
                    print("Ran into error creating creep: " + result)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new harvester named " + creep_name)
            elif num_builders < globals.MAX_BUILDERS and spawn.store.getUsedCapacity(RESOURCE_ENERGY) >= 250:
                creep_name = Game.time
                result = spawn.spawnCreep([WORK, CARRY, MOVE, MOVE], creep_name, { "memory": { "role": "builder"} })
                if result != OK:
                    print("Ran into error creating creep: " + result)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new builder named " + creep_name)
            """
        
    # Harvesting
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role == "harvester":
            harvester.run_harvester(creep, num_creeps)
        elif creep.memory.role == "builder":
            builder.run_builder(creep)

"""     
    # Run each creep
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        harvester.run_harvester(creep)

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]
        if not spawn.spawning:
            # Get the number of our creeps in the room.
            num_creeps = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName)
            # If there are no creeps, spawn a creep once energy is at 250 or more
            if num_creeps < 0 and spawn.room.energyAvailable >= 250:
                spawn.createCreep([WORK, CARRY, MOVE, MOVE])
            # If there are less than 15 creeps but at least one, wait until all spawns and extensions are full before
            # spawning.
            elif num_creeps < 15 and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable:
                # If we have more energy, spawn a bigger creep.
                if spawn.room.energyCapacityAvailable >= 350:
                    spawn.createCreep([WORK, CARRY, CARRY, MOVE, MOVE, MOVE])
                else:
                    spawn.createCreep([WORK, CARRY, MOVE, MOVE]) """



module.exports.loop = main
