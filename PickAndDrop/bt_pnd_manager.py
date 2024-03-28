from .bt_pnd_conditions import *
from .bt_pnd_actions import *

'''
followed https://github.com/ethz-asl/bt_fsm_comparison/blob/main/imgs/exp1_bt.svg
'''
def get_pnd_subtree(robot, objCoord, grid_world):
    check_delivery = DeliveryCondition(objCoord, grid_world, "CheckDelivery")
    check_hand = HandCondition("CheckHand")
    check_robot_at_src = RobotAtSrcCondition(robot.getCoords, objCoord, grid_world, "CheckRobotAtSrc")
    check_robot_at_dst = RobotAtDeliveryCondition(robot.getCoords, grid_world, "CheckRobotAtDst")

    move_to_src = MoveToSrc(robot, objCoord, "MoveToSrc")
    pick_obj = PickObject(robot, check_hand,  name="PickObject")
    drop_obj = PlaceObject(robot, check_hand, name="DropObject")
    move_to_dst = MoveToDelivery(robot, grid_world, objCoord, "MoveToDst")


    fallback_move_src = py_trees.composites.Selector("fallback_move_src", True)
    fallback_move_src.add_children([check_robot_at_src, move_to_src])

    sequence_pick_obj = py_trees.composites.Sequence("sequence_pick_obj", True)
    sequence_pick_obj.add_children([fallback_move_src, pick_obj])

    fallback_hand_condition = py_trees.composites.Selector("fallback_hand_condition", True)
    fallback_hand_condition.add_children([check_hand, sequence_pick_obj])

    fallback_delivery = py_trees.composites.Selector("fallback_delivery", True)
    fallback_delivery.add_children([check_robot_at_dst, move_to_dst])

    sequence_drop_obj = py_trees.composites.Sequence("sequence_drop_obj", True)
    sequence_drop_obj.add_children([fallback_hand_condition, fallback_delivery, drop_obj])

    root = py_trees.composites.Selector("FallbackRootPND", True)
    root.add_children([check_delivery, sequence_drop_obj])
    return root

