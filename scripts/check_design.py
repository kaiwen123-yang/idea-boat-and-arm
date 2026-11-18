#!/usr/bin/env python3
"""Check reference design arithmetic only. This does not run a simulator."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def positive_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive number")
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return value


def calculate(config: dict) -> dict:
    if config.get("status") != "DESIGN_ONLY":
        raise ValueError("This script expects the design-only configuration")
    hull = config["hull"]
    proxy = config["reference_proxy"]
    camera = config["camera"]
    length, width, height = [
        positive_number(x, "pontoon dimension") for x in hull["pontoon_size_m"]
    ]
    centers = hull["pontoon_centers_B_m"]
    if len(centers) != 2 or any(len(p) != 3 for p in centers):
        raise ValueError("The analytical reference assumes two box pontoons")
    if not all(math.isclose(a, -b, abs_tol=1e-12)
               for a, b in zip(centers[0], centers[1])):
        raise ValueError("The analytical reference assumes symmetric centers")
    if not all(math.isclose(p[2], 0.0, abs_tol=1e-12) for p in centers):
        raise ValueError("The reference assumes both pontoon centers at z=0")
    rho = positive_number(config["environment"]["water_density_kg_m3"], "water density")
    gravity = positive_number(config["environment"]["gravity_m_s2"], "gravity")
    base_mass = positive_number(hull["base_mass_excluding_arm_camera_kg"], "base mass")
    arm_mass = positive_number(proxy["arm_and_gripper_mass_kg"], "proxy arm mass")
    camera_mass = positive_number(proxy["camera_assembly_mass_kg"], "camera mass")
    assumed_camera_mass = camera["simulation_assumptions"]["assembly_mass_kg"]
    if not math.isclose(camera_mass, assumed_camera_mass, abs_tol=1e-12):
        raise ValueError("Proxy and simulated camera assembly mass disagree")
    mass = base_mass + arm_mass + camera_mass
    area = len(centers) * length * width
    draft = mass / (rho * area)
    if not 0 < draft < height:
        raise ValueError("Reference draft is outside the pontoon height")
    target = proxy["target"]
    tx, ty, tz = [
        positive_number(v, "target dimension") for v in target["size_m"]
    ]
    target_density = positive_number(target["density_kg_m3"], "target density")
    if target_density >= rho:
        raise ValueError("Reference target must float without external support")
    target_volume = tx * ty * tz
    target_mass = target_volume * target_density
    target_draft = target_mass / (rho * tx * ty)
    waterplane_roll_moment = sum(
        length * width**3 / 12 + length * width * p[1]**2 for p in centers
    )
    waterplane_pitch_moment = sum(
        width * length**3 / 12 + length * width * p[0]**2 for p in centers
    )
    dt = positive_number(config["backend"]["physics_dt_s"], "physics dt")
    control_dt = positive_number(config["backend"]["control_period_s"], "control period")
    if not math.isclose(control_dt / dt, round(control_dt / dt), abs_tol=1e-9):
        raise ValueError("Initial controller period must be an integer number of steps")
    fps = positive_number(camera["rgb"]["simulation_rate_hz"], "design RGB rate")
    vfov = positive_number(camera["simulation_assumptions"]["rgb_vertical_fov_deg"], "FOV")
    if vfov >= 180:
        raise ValueError("Perspective vertical FOV must be below 180 degrees")
    ideal_fy = camera["rgb"]["height"] / (2 * math.tan(math.radians(vfov) / 2))
    period = config["marine"]["wave_cases"][1]["period_s"]
    omega = 2 * math.pi / positive_number(period, "wave period")
    wave_number = omega**2 / gravity
    return {
        "check_scope": "DESIGN_ARITHMETIC_ONLY",
        "arithmetic_status": "OK",
        "simulation_run": False,
        "physical_acceptance_status": "NOT_RUN",
        "hardware_asset_binding": config["formal_scene"]["status"],
        "profile": "reference_proxy",
        "reference": {
            "waterplane_area_m2": area,
            "platform_mass_kg": mass,
            "draft_m": draft,
            "freeboard_m": height - draft,
            "hull_origin_z_m": height / 2 - draft,
            "target_volume_m3": target_volume,
            "target_mass_kg": target_mass,
            "target_draft_m": target_draft,
            "target_center_z_m": tz / 2 - target_draft,
            "target_freeboard_m": tz - target_draft,
            "target_weight_N": target_mass * gravity,
            "ideal_payload_draft_change_m": target_mass / (rho * area),
            "calibration_payload_draft_change_m":
                positive_number(proxy["calibration_payload_kg"], "calibration payload")
                / (rho * area),
            "heave_stiffness_N_per_m": rho * gravity * area,
            "waterplane_second_moment_roll_m4": waterplane_roll_moment,
            "waterplane_second_moment_pitch_m4": waterplane_pitch_moment,
            "deep_water_wave_number_per_m": wave_number,
            "deep_water_wavelength_m": 2 * math.pi / wave_number,
            "ideal_rgb_fy_pixels": ideal_fy,
            "physics_steps_per_rgb_frame": 1 / (dt * fps),
            "camera_requires_fractional_step_schedule":
                not math.isclose(1 / (dt * fps), round(1 / (dt * fps)), abs_tol=1e-9),
        },
        "limitations": [
            "No MuJoCo import, robot asset, force calculation or physics simulation.",
            "Reference proxy numbers are not Piper hardware specifications.",
            "Draft assumes horizontal symmetric waterplane; full-arm trim is separate.",
            "Camera FOV/mass are design assumptions, not DC1 calibration or weighing.",
            "No P1 case status is modified by this script."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path,
        default=Path(__file__).resolve().parents[1] / "configs" / "phase1_design.json"
    )
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        output = calculate(config)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Design check failed: {exc}\n")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
