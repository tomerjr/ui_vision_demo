import time, sys, yaml, pathlib, subprocess, signal, os
import cv2 as cv, numpy as np, pyautogui as pag

ROOT = pathlib.Path(__file__).parent
RES  = ROOT / "resources"
TIMEOUT    = 15         # seconds for wait/assert
CONFIDENCE = 0.7        # template-match threshold

def locate(img_path):
    """Return centre (x, y) of first match or None."""
    screen = pag.screenshot()
    scr_rgb = cv.cvtColor(np.array(screen), cv.COLOR_BGR2RGB)
    template = cv.imread(str(img_path))
    res = cv.matchTemplate(scr_rgb, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= CONFIDENCE)
    if loc[0].size:
        y, x = int(loc[0][0]), int(loc[1][0])
        h, w = template.shape[:2]
        return x + w // 2, y + h // 2
    return None

def wait_for(image, label):
    t0 = time.time()
    while time.time() - t0 < TIMEOUT:
        pos = locate(image)
        if pos:
            pag.moveTo(pos)  # cursor jumps to match centre
            return pos
        time.sleep(0.25)
    sys.exit(f"[FAIL] {label}: '{image}' not found within {TIMEOUT}s")

def bring_window_to_front(title_fragment="S I M  L A B"):
    """On Windows, activate the Tk window so PyCharm's console stays in background."""
    try:
        pag.getWindowsWithTitle(title_fragment)[0].activate()
    except Exception:
        pass  # not fatal on macOS/Linux

def main():
    # ---------- launch the dummy UI ----------
    dummy = subprocess.Popen([sys.executable, "dummy_app.py"])
    time.sleep(0.5)                 # give Tk a moment to render
    bring_window_to_front()

    try:
        plan = yaml.safe_load((ROOT / "test_plan.yaml").read_text())
        for step in plan:
            action, value = next(iter(step.items()))
            if action in ("wait_until", "click", "assert_seen"):
                img = ROOT / value
                if action == "wait_until":
                    wait_for(img, action)
                elif action == "click":
                    pos = wait_for(img, action)
                    pag.moveTo(pos); pag.click()
                else:  # assert_seen
                    wait_for(img, action)
            elif action == "type":
                pag.write(value, interval=0.05)
            else:
                sys.exit(f"[ERROR] Unknown action: {action}")
        print("[PASS] Test completed successfully.")
    finally:
        # --------- make sure the child Tk process exits ----------
        try:
            os.kill(dummy.pid, signal.SIGTERM)
        except Exception:
            pass

if __name__ == "__main__":
    pag.FAILSAFE = True  # move mouse to a screen corner to abort
    main()