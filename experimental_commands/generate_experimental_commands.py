def generate_experimental_commands(
    syringe_size: int,
    number_of_syringes: int,
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    volume_pump1: float,
    volume_pump2: float,
    volume_pump3: float,
    *,
    zero_tolerance: float = 1e-6,  # treat |x| <= zero_tol as zero
    log_skips: bool = True,
) -> List[List[str]]:
    """
    This will generate the experimental flow reaction commands for this reactor bed

    parameters:
    - syringe_size: The type of syringe being used for the harvard aparatus
    - number_of_syringes: The number of syringes loaded on the harvard aparatus syringe
    - flow_rate_pump1: Flow rate of harvard apparatus with our XYLO compound
    - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
    before it reaches the detector using the VICI M6 Pump 1
    - flow_rate_pump3: Flow rate of 0.1 M HCL water for diluting our compound
    before it reaches the UV-detector and after the reactor bed using the
    VICI M6 Pump 2
    - volume_pump1: Volume of Xylo compound to pump using harvard aparatus
    - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound before
    it reaches the reactor bed
    - volume_pump3: volume 0.1 M HCl water to dilute our Xylo compound solution
    before it reaches the UV-detector

    return:
    - commands: Experimental commands for reacting the flow reaction
    """

    def _is_zero(rate: float, vol: float) -> bool:
        return (abs(rate) <= zero_tolerance) or (abs(vol) <= zero_tolerance)

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [header]
    commands.append([
            "HarvardPump",
            "select_syringe",
            f"syringe={syringe_size},pump_id=1",
            f"The selected syringe size is {syringe_size}, loaded with {number_of_syringes} syringes",
            "",
            0.5,
        ]
    )
    commands.append([
            "HarvardPump",
            "infuse",
            f"volume={volume_pump1},rate={flow_rate_pump1},pump_id=1",
            f"The flow rate of our Xylo compund is {flow_rate_pump1} uL/min and volume is {volume_pump1}",
            "",
            0.5,
        ]
    )
    if not _is_zero(flow_rate_pump2, volume_pump2):
        commands.append(
            [
            "Pump",
            "dispensing",
            f"flow_rate={flow_rate_pump2}, " f"volume={volume_pump2}, pump_id=1",
            f"The flow rate of our Water is {flow_rate_pump2} uL/min and volume is {volume_pump2}",
            "",
            0.5,
        ]
        )

    if not _is_zero(flow_rate_pump3, volume_pump3):
        commands.append([
            "Pump",
            "dispensing",
            f"flow_rate={flow_rate_pump3}, volume={volume_pump3}, pump_id=2",
            f"The flow rate of our Water is {flow_rate_pump3} uL/min and volume is {volume_pump3}",
            "",
            0.5,
        ]
        )
    commands.append([
            "SYNC",
            "wait_for_pumps",
            "",
            "Waiting for XYLO and WATER pumps to complete",
            "",
            0.5,
        ]
    )
    commands.append([
            "HarvardPump",
            "stop",
            "pump_id=1",
            "The pump should have stopped but this is a safety check",
            "",
            0.5,
        ]
    )

    return commands

