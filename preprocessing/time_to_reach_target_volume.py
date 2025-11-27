def time_to_reach_target_volume(
    flow_rate: int,
    target_volume: int,
) -> float:
    """
    Time to flow the target volume based on the flow rate of the pumps

    parameters:
     - flow_rate: Measures the amount of fluid that travels through the pumps tubes in a given time
     - target_volume: Target Volume for the pumps to transfer out
    return:
     - time_target_volume_is_reached - Calculates time to flow total volume for the experiment
    """
    if flow_rate <= 0:
        raise ValueError("flow_rate must be > 0 to compute residence time.")

    time_target_volume_is_reached = (target_volume / flow_rate) * 60
    return time_target_volume_is_reached
