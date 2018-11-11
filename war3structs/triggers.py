from construct import *
from .common import *
from .patch.triggerdata import functions_parameter_counts

"""
  Formats: wtg
  Version: 7

  The triggers file contains the map's triggers, trigger categories and
  variables.
"""

TriggerCategory = Struct(
  "index" / Integer,
  "name" / String,
  "is_comment" / Integer
)

TriggerVariable = Struct(
  "name" / String,
  "type" / String,
  "unknown_field_1" / Integer, # always 1?
  "is_array" / Integer,
  "array_size" / Integer,
  "is_initialized" / Integer,
  "initial_value" / String
)

TriggerBlockType = Enum(Integer, EVENT=0, CONDITION=1, ACTION=2, FUNCTION_CALL=3)
TriggerBlockParameterSet = Array(lambda ctx: functions_parameter_counts[ctx.function_name], LazyBound(lambda: TriggerBlockParameter))

TriggerBlockParameter = Struct(
  "type" / Enum(Integer, PRESET=0, VARIABLE=1, FUNCTION=2, CONSTANT=3),
  "value" / String,
  "functions_count" / Integer,
  "functions" / Array(this.functions_count, LazyBound(lambda: TriggerBlock)),
  "array_indices_count" / Integer,
  "array_indices" / Array(this.array_indices_count, LazyBound(lambda: TriggerBlockParameter)),
)

TriggerIfThenElseBlock = Struct(
  "type" / TriggerBlockType,
  "branch_type" / Enum(Integer, IF=0, THEN=1, ELSE=2),
  "function_name" / String,
  "is_function_enabled" / Integer,
  "parameters" / TriggerBlockParameterSet,
  "child_blocks_count" / Integer,
  "child_blocks" / Array(this.child_blocks_count, LazyBound(lambda: Select(TriggerIfThenElseBlock, TriggerBlock)))
)

TriggerBlock = Struct(
  "type" / TriggerBlockType,
  "function_name" / String,
  "is_function_enabled" / Integer,
  "parameters" / TriggerBlockParameterSet,
  "child_blocks_count" / Integer,
  "child_blocks" / Array(this.child_blocks_count, LazyBound(lambda: Select(TriggerIfThenElseBlock, TriggerBlock)))
)

Trigger = Struct(
  "name" / String,
  "description" / String,
  "is_comment" / Integer,
  "is_enabled" / Integer,
  "is_custom_text_trigger" / Integer,
  "is_turned_off" / Integer,
  "is_init" / Integer,
  "category_index" / Integer,
  "blocks_count" / Integer,
  "blocks" / Array(this.blocks_count, TriggerBlock)
)

TriggersFile = Struct(
  "file_id" / Const(b"WTG!"),
  "version" / Integer,
  "trigger_categories_count" / Integer,
  "trigger_categories" / Array(this.trigger_categories_count, TriggerCategory),
  "unknown_field_1" / Integer, # ?
  "trigger_variables_count" / Integer,
  "trigger_variables" / Array(this.trigger_variables_count, TriggerVariable),
  "triggers_count" / Integer,
  "triggers" / Array(this.triggers_count, Trigger)
)
