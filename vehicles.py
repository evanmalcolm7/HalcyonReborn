from regions import Region, Celestial

from botInterface import Payload

from files import get_file, save_file

from math import sqrt

# TODO: come up with some sort of unique ID system
# TODO: maybe change all these xy attributes to just giving the Region

class Vehicle:

    def __init__(self, owner, xy):
        self.owner = owner # the Player object that owns this
        self.xy = xy # the initial coordinates of this halcyon
        self.id = self.owner.upper() + (type(self).__name__).lower() # e.g. EVANhalcyon
        # get all the functions that can be "cast"-- abilities in game terms
        self.abilities = [f for f in dir(type(self)) if not f.startswith('priv') and not f.startswith('_')]
        # store self into Regions.pickle
        Regions = get_file('Regions.pickle')
        Regions[self.xy].content[self.id] = self
        save_file(Regions, 'Regions.pickle')

    def priv_change_region(self, new_region_xy):
        # remove self from old region
        Regions = get_file('Regions.pickle')
        del Regions[self.xy].content[str(self)]
        # add self to new region
        new_region = Regions[new_region_xy]
        new_region.content[str(self)] = self
        save_file(Regions, 'Regions.pickle')

    def inspect(self):
        messages = [f'A {type(self).__name__} belonging to {self.owner}.',
                    f'It is currently in the region {self.xy}',
                    f'It has the following abilities: {self.abilities}']
        return Payload(self, messages)

class Halcyon(Vehicle):

    def __init__(self, owner, xy):
        super().__init__(owner, xy)

    def __str__(self):
        return f"{self.owner}'s Halcyon"

    def calc_slingshot(self, celest_1, celest_2):
        ### * bot-facing function * ###
        # calculates a fast path between two celestials
        # first, we have to check that both celestials exist
        Celestials = get_file('Celestials.pickle')
        try:
            c1 = Celestials[celest_1]
            c2 = Celestials[celest_2]
        except KeyError as e:
            return f"The indicated celestial {e} does not exist"
        # now we send out a Payload object to the bot
        return Payload(self, ['Hello',], isTaskMaker=True, taskDuration=1,
                        onCompleteFunc=self.priv_create_slingshot, onCompleteArgs = [c1, c2])

    def priv_create_slingshot(self, c1, c2):
        # get the starting and ending region of space
        Regions = get_file('Regions.pickle')
        start_region = Regions[c1.xy]
        end_region = Regions[c2.xy]
        # create a Slingshot Path Terminus in each spot
        start_region.content['Slingshot Path Terminus'] = self.priv_SPathTerminus(c1.xy, end_region)
        end_region.content['Slingshot Path Terminus'] = self.priv_SPathTerminus(c2.xy, start_region)
        save_file(Regions, 'Regions.pickle')

    class priv_SPathTerminus: # inner class woah fancy

        def __init__(self, xy, linkRegion):
            self.xy = xy
            self.linkRegion = linkRegion

        def __str__(self):
            return f"A Slingshot Path, linked to {self.linkRegion}"

        def priv_landing_func(self, landing_obj):
            # now, we get the distance between each celestial (in millions of miles)
            distance = sqrt( ((self.xy[0]-self.linkRegion.xy[0])**2)+((self.xy[1]-self.linkRegion.xy[1])**2) ) 
            # divide that distance by the slingshot travel rate
            travel_time = distance / 25
            return Payload(self, ['Hello'], isTaskMaker= True, taskDuration=travel_time,
                            onCompleteFunc = landing_obj.priv_change_region, onCompleteArgs = self.linkRegion)


# Region ( (0,0) )
# x = Halcyon( 'Breq', (0, 0) )
# print(get_file('Regions.pickle')[(0,0)].content['BREQhalcyon'])
# Region( (25, 0 ) )
# x = Halcyon( 'Breq', (0, 0) )
# Primus = Celestial( 'Primus', (0, 0) )
# Secondus = Celestial( 'Secondus', (25, 0) )

# x.create_slingshot(Primus, Secondus)

# Regions = get_file('Regions.pickle')
# a = Regions[ (0, 0) ].content[ "BREQhalcyon" ].abilities
# print(a)
# Regions = get_file('Regions.pickle')
# print(Regions[(0,0)].content, Regions[ (25,0) ].content)