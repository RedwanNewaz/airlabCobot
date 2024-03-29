from .bt_pnd_conditions import *
from .bt_pnd_actions import *

'''
followed https://github.com/ethz-asl/bt_fsm_comparison/blob/main/imgs/exp1_bt.svg
'''
def get_pnd_subtree(robot, grid_world):
    check_delivery = DeliveryCondition(grid_world.objCoord, robot, grid_world, "CheckDelivery")
    check_hand = HandCondition(robot, "CheckHand")

    move_to_src = MoveToSrc(robot, grid_world.objCoord, "MoveToSrc")
    pick_obj = PickObject(robot, check_hand,  name="PickObject")
    drop_obj = PlaceObject(robot,  grid_world.objCoord, grid_world, name="DropObject")
    move_to_dst = MoveToDelivery(robot, grid_world, grid_world.objCoord, "MoveToDst")

    check_robot_at_src = RobotAtSrcCondition(robot, grid_world.objCoord, grid_world, "CheckRobotAtSrc")
    check_robot_at_dst = RobotAtDeliveryCondition(robot, grid_world.objCoord, grid_world, "CheckRobotAtDst")



    fallback_move_src = py_trees.composites.Selector("fallback_move_src", False)
    fallback_move_src.add_children([check_robot_at_src, move_to_src])

    sequence_pick_obj = py_trees.composites.Sequence("sequence_pick_obj", False)
    sequence_pick_obj.add_children([fallback_move_src, pick_obj])

    fallback_hand_condition = py_trees.composites.Selector("fallback_hand_condition", False)
    fallback_hand_condition.add_children([check_hand, sequence_pick_obj])

    fallback_delivery = py_trees.composites.Selector("fallback_delivery", False)
    fallback_delivery.add_children([check_robot_at_dst, move_to_dst])

    sequence_drop_obj = py_trees.composites.Sequence("sequence_drop_obj", False)
    sequence_drop_obj.add_children([fallback_hand_condition, fallback_delivery, drop_obj])

    root = py_trees.composites.Selector("FallbackRootPND", False)
    root.add_children([check_delivery, sequence_drop_obj])
    return root

