import serial, time

PORT = "COM14"          # change if needed
ADDR = 1               # pump address (1–8)

# >>> IMPORTANT: set this after a quick calibration <<<
# Measure mL delivered in 60 s at a known rpm (e.g., 20.00 rpm).
# Then ML_PER_REV = measured_ml / rpm
ML_PER_REV = 0.085     # <-- placeholder example; replace with YOUR measured value

ser = serial.Serial(PORT, 9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)
time.sleep(5)  # pump's RS-232 wakes up a few seconds after power-on

def send(cmd: str) -> str:
    """Send ASCII command (without CR) and return reply as string."""
    ser.reset_input_buffer()
    ser.write((cmd + '\r').encode('ascii'))
    resp = ser.read_until(b'\r').decode('ascii', errors='ignore').strip()
    # optional LF may follow
    ser.read(1)
    return resp

def set_direction_cw(addr=ADDR):
    return send(f"{addr}J")  # clockwise (use 'K' for CCW)

def start(addr=ADDR):
    return send(f"{addr}H")

def stop(addr=ADDR):
    return send(f"{addr}I")

def set_rpm(addr: int, rpm: float) -> str:
    """
    Set motor speed. Device accepts hundredths of rpm (0.01 rpm steps), 6 digits, zero-padded.
    Returns '*' on success.
    """
    v = int(round(rpm * 100))          # quantize to 0.01 rpm
    return send(f"{addr}S{v:06d}")     # e.g., 2.00 rpm -> 'S000200'

def get_rpm(addr: int) -> float:
    """Query current rpm as float."""
    return float(send(f"{addr}S"))

def set_flow_ml_min(addr: int, flow_ml_min: float):
    """
    Set desired flow in mL/min by converting to rpm.
    Returns (ack, commanded_rpm, achieved_flow_ml_min).
    """
    if ML_PER_REV <= 0:
        raise ValueError("ML_PER_REV is not set. Calibrate first.")
    rpm = round(flow_ml_min / ML_PER_REV, 2)   # quantize to 0.01 rpm
    ack = set_rpm(addr, rpm)
    achieved = round(rpm * ML_PER_REV, 4)      # what the quantized rpm actually delivers
    return ack, rpm, achieved

def get_flow_ml_min(addr: int) -> float:
    """Compute current mL/min from rpm and ML_PER_REV."""
    rpm = get_rpm(addr)
    return round(rpm * ML_PER_REV, 4)

def flow_resolution_ml_min() -> float:
    """Minimum achievable flow step from 0.01 rpm quantization."""
    return round(0.01 * ML_PER_REV, 6)

def compute_ml_per_rev_from_test(measured_ml: float, test_rpm: float, duration_s: float = 60.0) -> float:
    """
    Helper to compute ML_PER_REV from a calibration run.
    If you run at test_rpm for duration_s and collect measured_ml, then:
      ml/rev = measured_ml / (test_rpm * duration_s/60)
              = measured_ml / test_rpm   (when duration_s == 60)
    """
    return measured_ml / (test_rpm * (duration_s / 60.0))

# ---------- Example usage ----------
if __name__ == "__main__":
    try:
        print(set_direction_cw())                           # '*'
        ack, rpm_cmd, achieved = set_flow_ml_min(ADDR, 0.030)
        print(ack, f"(commanded {rpm_cmd:.2f} rpm, ~{achieved:.4f} mL/min)")
        print(start())                                      # '*'
        time.sleep(3)
        print("rpm =", get_rpm(ADDR))
        print("approx flow (mL/min) =", get_flow_ml_min(ADDR))
        print("flow resolution (mL/min) ≈", flow_resolution_ml_min())
        print(stop())                                       # '*'
    finally:
        ser.close()

