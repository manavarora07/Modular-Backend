"""
Builds a natural-language features_text string from a normalized product dict.
This text is used as the input to the OpenAI embedding model.
"""


def build_features_text(product: dict) -> str:
    """
    Convert a normalized product spec dict into a human-readable sentence.
    Only includes fields that are present (non-None) to keep the text clean.
    """
    category = product.get("category", "semiconductor")
    name = product.get("product_name", "")
    parts = [f"{name} {category}"]

    # --- Microcontroller fields ---
    arch = product.get("architecture")
    if arch:
        parts.append(f"architecture {arch}")

    flash = product.get("flash_kb")
    if flash is not None:
        parts.append(f"{int(flash)}KB flash memory")

    ram = product.get("ram_kb")
    if ram is not None:
        parts.append(f"{int(ram)}KB RAM")

    gpio = product.get("gpio_pins")
    if gpio is not None:
        parts.append(f"{gpio} GPIO pins")

    vmin = product.get("voltage_min")
    vmax = product.get("voltage_max")
    if vmin is not None and vmax is not None:
        parts.append(f"operating voltage {vmin}V to {vmax}V")
    elif vmin is not None:
        parts.append(f"operating voltage {vmin}V")

    interfaces = product.get("interfaces")
    if interfaces:
        parts.append(f"interfaces {interfaces}")

    speed = product.get("max_speed_mhz")
    if speed is not None:
        parts.append(f"{int(speed)}MHz max clock")

    # --- Sensor fields ---
    sensor_type = product.get("sensor_type")
    if sensor_type:
        parts.append(f"sensor type {sensor_type}")

    mrange = product.get("measurement_range")
    if mrange:
        parts.append(f"measurement range {mrange}")

    accuracy = product.get("accuracy")
    if accuracy:
        parts.append(f"accuracy {accuracy}")

    output_type = product.get("output_type")
    if output_type:
        parts.append(f"output {output_type}")

    # --- Power IC fields ---
    topology = product.get("topology")
    if topology:
        parts.append(f"topology {topology}")

    out_v = product.get("output_voltage")
    if out_v:
        parts.append(f"output voltage {out_v}")

    out_i = product.get("output_current_a")
    if out_i is not None:
        parts.append(f"output current {out_i}A")

    sw_freq = product.get("switching_frequency_khz")
    if sw_freq is not None:
        parts.append(f"switching frequency {int(sw_freq)}kHz")

    efficiency = product.get("efficiency")
    if efficiency:
        parts.append(f"efficiency {efficiency}")

    # --- Memory fields ---
    mem_type = product.get("memory_type")
    if mem_type:
        parts.append(f"memory type {mem_type}")

    cap = product.get("capacity_mb")
    if cap is not None:
        parts.append(f"capacity {cap}MB")

    mem_speed = product.get("speed")
    if mem_speed:
        parts.append(f"speed {mem_speed}")

    # --- Shared fields ---
    pkg = product.get("package_type")
    if pkg:
        parts.append(f"package {pkg}")

    temp = product.get("temp_range")
    if temp:
        parts.append(f"temperature range {temp}")

    interface = product.get("interface")
    if interface:
        parts.append(f"interface {interface}")

    return ", ".join(parts) + "."
