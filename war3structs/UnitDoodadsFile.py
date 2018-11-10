from construct import *
from war3structs.common import *
from war3structs.DoodadsFile import DoodadVisibilityFlags, DoodadItemSet

"""
  Formats: doo
  Version: 8

  The unit doodads file describes units and items present on the map.
  It differs from the doodads file even though they use the same "file
  extension." It is used for the war3mapUnits.doo file, as opposed to
  war3map.doo.
"""

UnitDoodadInventoryItem = Struct(
  "slot_index" / Integer,
  "item_id" / ByteId
)

UnitDoodadAbilityModification = Struct(
  "ability_id" / ByteId,
  "is_active" / Integer, # for autocast abilities
  "level" / Integer
)

UnitDoodadRandomItemClass = Enum(Byte,
  ANY_CLASS     = 0,
  PERMANENT     = 1,
  CHARGED       = 2,
  POWER_UP      = 3,
  ARTIFACT      = 4,
  PURCHASABLE   = 5,
  CAMPAIGN      = 6,
  MISCELLANEOUS = 7
)

UnitDoodadRandomUnit = Struct(
  "type" / Enum(Integer,
    ANY               = 0,
    FROM_MAP_TABLE    = 1,
    FROM_CUSTOM_TABLE = 2
  ),
  "properties" / Switch(this.type, {
    "ANY" : Struct(
      "level" / Byte[3], # -1 = any level
      "item_class" / UnitDoodadRandomItemClass
    ),
    "FROM_MAP_TABLE" : Struct(
      "table_index" / Integer,
      "position_index" / Integer # the position here must be of the correct type
                                 # (unit, building, item) based on what the doodad
                                 # is
    ),
    "FROM_CUSTOM_TABLE" : Struct(
      "units_count" / Integer,
      "units" / Array(this.units_count, Struct(
        "unit_id" / ByteId, # this can use the "random id" type of id
                            # units:
                            # if the first three bytes are "Y", "Y" and "U"
                            # then the fourth byte denotes the unit level:
                            # "/" for any level, chr(48 + level) for a
                            # specific level
                            # items:
                            # if the first byte is "Y" and the third is "I"
                            # then the second byte denotes the item type: "Y"
                            # for any class, "i" to "o" for a specific class,
                            # in the same order as seen in the class enum
                            # the fourth byte denotes the item level: "/" for
                            # any level, chr(48 + level) for a specific level
                            # buildings:
                            # if the first three bytes are "Y", "Y" and "B"
                            # then it's a random building: it must (probably)
                            # always be "YYB/" since buildings have no levels
                            # or classes
        "chance_percent" / Integer
      ))
    )
  })
)

UnitDoodad = Struct(
  "unit_id" / ByteId,
  "variation" / Integer,
  "pos_x" / Float,
  "pos_y" / Float,
  "pos_z" / Float,
  "rotation" / Float, # in radians
  "scale_x" / Float,
  "scale_y" / Float,
  "scale_z" / Float,
  "visibility" / DoodadVisibilityFlags,
  "owner_player_id" / Integer,
  "unknown_property_1" / Byte,
  "unknown_property_2" / Byte,
  "hitpoints" / Integer, # -1 for default
  "manapoints" / Integer, # -1 for default, 0 if the unit has no mana
  "dropped_item_table_index" / Integer, # -1 for no item drop from the map item tables
  "dropped_item_sets_count" / Integer, # only if above is -1
  "dropped_item_sets" / Array(this.dropped_item_sets_count, DoodadItemSet),
  "gold" / Integer,
  "target_acquisition_range" / Float, # -1 for normal (500), -2 for camp (200).
                                      # why float? can this be arbitrary?
  "hero_level" / Integer,
  "hero_strength" / Integer,
  "hero_agility" / Integer,
  "hero_intelligence" / Integer,
  "inventory_items_count" / Integer,
  "inventory_items" / Array(this.inventory_items_count, UnitDoodadInventoryItem),
  "ability_modifications_count" / Integer,
  "ability_modifications" / Array(this.ability_modifications_count, UnitDoodadAbilityModification),
  "random_unit" / IfThenElse(lambda ctx: ctx.unit_id == b"uDNR" or ctx.unit_id == b"bDNR" or ctx.unit_id == b"iDNR",
    UnitDoodadRandomUnit,
    Sequence(Const(0, Integer), Const(1, Integer))
  ),
  "waygate_custom_team_color" / Integer, # -1 for none
  "waygate_destination_region_index" / Integer, # -1 for deactivated, otherwise the index of the
                                                # target rect in the RegionsFile
  "index" / Integer
)

UnitDoodadsFile = Struct(
  "file_id" / Const(b"W3do"),
  "version" / Integer,
  "subversion" / Integer, # ?
  "units_count" / Integer,
  "units" / Array(this.units_count, UnitDoodad)
)
