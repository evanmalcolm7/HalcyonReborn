from random import choice, random
from files import save_file, get_file
from botInterface import Payload
from players import Player


class Region:
    # each region is a cube of space along the galactic plane
    # 1milx1milx1mil KM
    # there are 500 regions in each cardinal direction from the sun
    def __init__(self, xy):
        self.xy = xy
        self.content = {}
        # add self to the Regions dict
        Regions = get_file('Regions.pickle')
        Regions[self.xy] = self
        save_file(Regions, 'Regions.pickle')

    def __str__(self):
        return str(self.xy)

    def scan(self):
        prefix = ['This region contains the following entities:']
        content_list = [str(obj) for obj in self.content.values()]
        messages = prefix + content_list
        return Payload(self, messages)

    def check_vision(self, viewer_uid):
        '''Checks each entity in region, returns if <viewer_uid> owns any'''
        Players = get_file('Players.pickle')
        try:
            viewer = Players[viewer_uid]
        except KeyError as e:
            # generally if that player object hasn't been created
            print(f'check_vision KeyError {e}')
            return False
        for entity in self.content.values():
            try:
                if entity.owner.uid == viewer.uid:
                    return True
            except AttributeError as e:
                # generally, because there's an entity with no owner
                print(e)
        return False


class Celestial:
    # any sort of non-actively propelled object in space

    def __init__(self, name, xy, territories=None):
        self.name = name
        self.xy = xy
        self.territories = territories
        # add self to the region designated by xy
        Regions = get_file('Regions.pickle')
        Regions[xy].content[name] = self
        save_file(Regions, 'Regions.pickle')
        # add self to celestial storage
        Celestials = get_file('Celestials.pickle')
        Celestials[self.name] = self
        save_file(Celestials, 'Celestials.pickle')

    def __str__(self):
        return self.name

    def landed_on(self, entity_id, target_territory):
        '''Function that is called when this celestial is landed on

        entity_id -- The ID of the entity that is lending on this celestial
        target_territory -- The territory this entity will land'''
        # * Note that this "sucks in" the landing_entity * #
        # * Vs. the entity actually landing * #
        # * The celestial is doing all the work * #
        Regions = get_file('Regions.pickle')
        Region = Regions[self.xy]
        # add the entity to the territory
        entity_obj = Region.content[entity_id]
        self.territories[entity_id] = entity_obj
        # delete the entity from the region
        del Region.content[entity_id]
        # return the payload for the landing
        messages = [f'{entity_obj} has landed on the {target_territory} region of {self}.']
        return Payload(self, messages)


class Planet(Celestial):

    def __init__(self, name, xy):
        super().__init__(name, xy)
        self.territories = self.gen_territories()

    def __str__(self):
        return self.name

    def inspect(self):
        pass

    def gen_territories(self):
        TERRITORY_LABELS = ('North', 'Northeast', 'East', 'Southeast',
                            'South', 'Southwest', 'West', 'Northwest')
        # this is the part that randomly assigns the biomes to territories
        territories = {}
        for lab in TERRITORY_LABELS:
            # create an Territory object (with random biomes) and append it
            territories[lab] = Territory(self, lab)
        return territories


class Territory:

    # TODO | UNIQUES: do later
    # TODO | special case for NONE: polar, desert, wastes

    def __init__(self, parent, label, content=None, has_biomes=True):
        self.parent = parent  # the object the territory is attached to
        self.label = label  # the reference label of the territory
        self.content = content  # what's in this territory
        self.description = ''
        self.has_biomes = has_biomes
        # now, we randomly select what resources this territory will have
        self.resources = {}
        RESOURCE_BIOMES = {'Wood': ('Forest', 'Jungle', 'Taiga'),
                           'Stone': ('Hill', 'Steppe', 'Mountain'),
                           'Metal': ('Cave', 'Crevice', 'Canyon')
                           }
        if self.has_biomes:
            i = 0
            descs = set([])  # use a set to make sure there's no repeats
            while i <= 0.75:
                # pick a random resource from the list to add
                res = choice(list(RESOURCE_BIOMES))
                # pick a random biome associated with that choice
                descs.add(choice(RESOURCE_BIOMES[res]))
                try:
                    # try to add 5 of the resource
                    self.resources[res] += 5
                except KeyError:
                    # if it fails, there's none of that resource
                    # therefore we should set it to 5 instead
                    self.resources[res] = 5
                i += random()
            for d in sorted(list(descs), reverse=True):
                self.description += d
                self.description += ' '
            # remove the extraneous extra space and 'y'
            self.description = self.description[:-1]
            self.description += 's'
