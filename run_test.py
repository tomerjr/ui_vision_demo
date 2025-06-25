import time, sys, subprocess, signal, os, pathlib
import cv2 as cv, numpy as np, pyautogui as pag, yaml

ROOT        = pathlib.Path(__file__).parent.resolve()
RES         = ROOT / "resources"
PLAN_PATH   = ROOT / "test_plan.yaml"
DUMMY_PATH  = ROOT / "dummy_app.py"
TIMEOUT     = 15
CONFIDENCE  = 0.95

# ── basic helpers ────────────────────────────────────────────────────
def locate(img_path, conf):
    screen = cv.cvtColor(np.array(pag.screenshot()), cv.COLOR_BGR2RGB)

    tmpl = cv.imread(str(img_path), cv.IMREAD_UNCHANGED)
    if tmpl is None:
        sys.exit(f"[ERR] cannot read {img_path}")
    if tmpl.shape[2] == 4:                       # drop alpha if present
        tmpl = cv.cvtColor(tmpl, cv.COLOR_BGRA2BGR)

    res = cv.matchTemplate(screen, tmpl, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)   # max_loc = (x, y)

    if max_val < conf:
        return None

    x, y = max_loc                               # ← correct order
    h, w = tmpl.shape[:2]
    return x + w // 2, y + h // 2                # (x, y) centre

def wait_for(img_path, label,conf=CONFIDENCE):
    t0 = time.time()
    while time.time() - t0 < TIMEOUT:
        pos = locate(img_path, conf)          # pass down
        if pos:
            return pos
        time.sleep(0.25)
    sys.exit(f"[FAIL] {label}: '{img_path.name}' not seen in {TIMEOUT}s")

def click_then_type(pos, text):
    pag.moveTo(pos); pag.click()
    pag.hotkey("ctrl", "a")
    pag.typewrite(text, interval=0.05)

def active_window_size() -> tuple[int, int]:
    """Return (width, height) of the active window; fall back to full screen."""
    try:
        win = pag.getActiveWindow()          # works on Win/Mac/Linux in PyAutoGUI ≥ 0.9
        return win.width, win.height
    except Exception:
        return pag.size()                    # fallback: full-screen resolution

# ── the YAML walker ──────────────────────────────────────────────────
def run_plan(plan_path: pathlib.Path):
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    for step in plan:
        action, value = next(iter(step.items()))

        # --- new compound step: fill ----------------------------------
        if action == "fill":
            tmpl = ROOT / value["template"]  # label template (same key name!)
            text = value["text"]
            label_pos = wait_for(tmpl, "fill")  # (cx, cy) of the label

            if "offset_ratio" in value:  # relative to window
                rx, ry = value["offset_ratio"]
                win_w, win_h = active_window_size()
                offx, offy = int(rx * win_w), int(ry * win_h)

            elif "offset_label_ratio" in value:  # relative to label image
                rlx, rly = value["offset_label_ratio"]
                tmpl_img = cv.imread(str(tmpl), cv.IMREAD_UNCHANGED)
                if tmpl_img.shape[2] == 4:  # drop alpha if any
                    tmpl_img = cv.cvtColor(tmpl_img, cv.COLOR_BGRA2BGR)
                h_lbl, w_lbl = tmpl_img.shape[:2]
                offx, offy = int(rlx * w_lbl), int(rly * h_lbl)

            else:  # fixed pixels fallback
                offx, offy = value.get("offset", [0, 0])

            target = (label_pos[0] + offx, label_pos[1] + offy)
            click_then_type(target, text)
            continue
        # --------------------------------------------------------------

        if action in ("wait_until", "click", "assert_seen"):
            # Accept either plain string or dict with extra keys
            if isinstance(value, str):
                img_path = ROOT / value
                local_conf = CONFIDENCE
            elif isinstance(value, dict):
                img_path = ROOT / value["template"]
                local_conf = value.get("confidence", CONFIDENCE)
            else:
                sys.exit(f"[ERROR] Invalid value for {action}: {value}")

            # wait / click / assert logic
            if action == "wait_until":
                wait_for(img_path, action, local_conf)
            elif action == "click":
                pos = wait_for(img_path, action, local_conf)
                pag.moveTo(pos);
                pag.click()
            else:  # assert_seen
                wait_for(img_path, action, local_conf)
            continue
        elif action == "type":
            pag.typewrite(value, interval=0.05)
        else:
            sys.exit(f"[ERROR] Unknown action: {action}")

# ── entry-point ─────────────────────────────────────────────────────
def main():
    dummy = subprocess.Popen([sys.executable, str(DUMMY_PATH)])
    time.sleep(0.6)               # let Tk render
    pag.FAILSAFE = True
    try:
        run_plan(PLAN_PATH)
        print("[PASS] Test completed successfully.")
    finally:
        try:
            os.kill(dummy.pid, signal.SIGTERM)
        except Exception:
            pass

if __name__ == "__main__":
    main()
