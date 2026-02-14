# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Calculates the time required to reach a target volume on the reactor bed.
"""

def time_to_reach_target_volume(
    reactor_bed_flow_rate: int,
    volume_to_flow_through_the_reactor_bed: int,
) -> float:
    """
    Time to flow the target volume based on the flow rate of the pumps

    parameters:
     - reactor_bed_flow_rate: Measures the amount of fluid that travels 
       through the pumps tubes in a given time
     - volume_to_flow_through_the_reactor_bed: Target Volume for the 
       pumps to flow through the reaction bed
    return:
     - time_target_volume_is_reached - Calculates time to flow total volume 
       for the experiment
    """
    if reactor_bed_flow_rate <= 0:
        raise ValueError("reactor_bed_flow_rate must be > 0 to compute residence time.")

    time_target_volume_is_reached = (
        volume_to_flow_through_the_reactor_bed / reactor_bed_flow_rate
    ) * 60
    
    return time_target_volume_is_reached
