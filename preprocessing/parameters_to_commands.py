def parameters_to_commands(
    flow_rate_uL_per_min: float,
    concentration: float,
    stock_concentration_uM: float,
    target_absorbance_in_the_uv_detector: float,
    max_absorbance_concentration_uM_uv_detector: float,
    volume_uL: int,
    number_of_syringes: int,
) -> Tuple[int, int, int, int, int, int]:
    """
    Generates instrument commands based on the recommendations from the bayesian optimizer

    parameters:
     - flow_rate: total flow rate when going through our reaction bed
     - concentration: Concentration of our system when going through our reaction bed
     - stock_concentration_uM:
     - target_absorbance_in_the_UV_detector: Sets the target absorbance the pumps
     should dilute to using
     the UV detector
     - max_absorbance_concentration_uM_UV_detector:
     - volume: total volume to go through our reaction bed
     - number_of_syringes: Tells the code, how many syringes are currently being used within the code

    return:
     - flow_rate_pump1: Rate to flow pump containing the Xylo compound
     - flow_rate_pump2: Rate to flow pump 0.1 M HCl Water diluting Xylo compound for
     the reaction bed
     - flow_rate_pump3: Rate to flow pump 0.1 M HCl Water diluting Xylo compound for
     the UV detector
     - volume_pump1: Volume to flow of Xylo compound through the pumps
     - volume_pump2: Volume of 0.1 M HCl water diluting Xylo compound for the reaction bed
     - volume_pump3: Volume of 0.1 M HCl Water diluting Xylo compound for the UV detector
    """
    if flow_rate_uL_per_min <= 0:
        raise ValueError("flow_rate must be > 0 µL/min.")
    if volume_uL <= 0:
        raise ValueError("volume must be > 0 µL.")
    if not (0.0 <= concentration <= 1.0):
        raise ValueError("concentration must be in [0, 1].")
    if number_of_syringes <= 0:
        raise ValueError("number_of_syringes must be >= 1.")

    # We are using two different pumps to control concentration and volume and is need to
    # help us control the conc.
    flow_rate_pump1_uL_per_min = (flow_rate_uL_per_min * concentration) / number_of_syringes
    volume_pump1_uL = (volume_uL * concentration) / number_of_syringes

    flow_rate_pump2_uL_per_min = flow_rate_uL_per_min * (1 - concentration)
    volume_pump2_uL = volume_uL * (1 - concentration)

    # Concentration in reactor stream (after first dilution):
    reactor_bed_concentration_uM = concentration * stock_concentration_uM

    # Desired concentration at detector from absorbance target:
    cuvette_concentration_uM = (
            max_absorbance_concentration_uM_uv_detector * target_absorbance_in_the_uv_detector
    )

    if cuvette_concentration_uM <= 0:
        raise ValueError("Target absorbance × max detector concentration must be > 0.")

    # If reactor is already <= target, no extra dilution needed
    if reactor_bed_concentration_uM <= cuvette_concentration_uM:
        flow_rate_pump3_uL_per_min = 0
        volume_pump3_uL = 0
    else:
        # Ratio of total flow to reactor flow needed to reach target must be ratio>1
        ratio = reactor_bed_concentration_uM / cuvette_concentration_uM
        reactor_bed_flow_rate_uL_per_min = flow_rate_pump1_uL_per_min + flow_rate_pump2_uL_per_min
        # Compute pump3 flow so that Q_total = r * Q_reactor
        cuvette_flow_rate_uL_per_min = reactor_bed_flow_rate_uL_per_min * ratio
        flow_rate_pump3_uL_per_min = max(0.0, cuvette_flow_rate_uL_per_min - reactor_bed_flow_rate_uL_per_min)
        # Apply same ratio to volumes: V_total = r * V_reactor => V_pump3 = (r-1)*V_reactor
        reactor_bed_volume_uL = volume_pump1_uL + volume_pump2_uL
        volume_pump3_uL = max(0.0, (ratio - 1.0) * reactor_bed_volume_uL)

    return (
        int(round(flow_rate_pump1_uL_per_min)), int(round(volume_pump1_uL)),
        int(round(flow_rate_pump2_uL_per_min)), int(round(volume_pump2_uL)),
        int(round(flow_rate_pump3_uL_per_min)), int(round(volume_pump3_uL)),
    )
