# sudoku_to_csv.py
import argparse
import csv
import os
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pytesseract


# -------------------- Geometry helpers --------------------
def order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]       # top-left
    rect[2] = pts[np.argmax(s)]       # bottom-right
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]       # top-right
    rect[3] = pts[np.argmax(d)]       # bottom-left
    return rect


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array(
        [[0, 0],
         [maxWidth - 1, 0],
         [maxWidth - 1, maxHeight - 1],
         [0, maxHeight - 1]], dtype="float32"
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped, M, rect


def find_puzzle_contour(gray: np.ndarray) -> Optional[np.ndarray]:
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thr = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    thr = cv2.bitwise_not(thr)

    contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32)
    return None


# -------------------- Cell extraction & OCR --------------------
def split_into_cells(warped_gray: np.ndarray) -> List[np.ndarray]:
    H, W = warped_gray.shape[:2]
    side = min(H, W)
    warped_gray = warped_gray[:side, :side]
    step = side // 9
    cells = []
    for r in range(9):
        for c in range(9):
            cell = warped_gray[r * step:(r + 1) * step, c * step:(c + 1) * step]
            m = int(0.12 * step)  # trim borders to avoid grid lines
            cell = cell[m:step - m, m:step - m]
            cells.append(cell)
    return cells


def is_cell_empty(cell_gray: np.ndarray, empty_threshold: float = 0.02) -> Tuple[bool, float]:
    # Otsu + invert → count white pixels as ink
    th = cv2.threshold(cell_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    nz = cv2.countNonZero(th)
    area = th.shape[0] * th.shape[1]
    ratio = (nz / float(area)) if area else 0.0
    return (ratio < empty_threshold), ratio


def read_digit(cell_gray: np.ndarray, tesseract_cmd: Optional[str] = None) -> int:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    th = cv2.threshold(cell_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8), iterations=1)

    config = "--oem 1 --psm 10 -c tessedit_char_whitelist=0123456789"
    txt = pytesseract.image_to_string(th, config=config)
    digits = [ch for ch in txt if ch.isdigit()]
    if not digits:
        return 0

    # choose most frequent digit
    counts = {}
    for ch in digits:
        counts[ch] = counts.get(ch, 0) + 1
    d = int(max(counts, key=counts.get))
    return d if 1 <= d <= 9 else 0


def ocr_grid(warped_gray: np.ndarray, tesseract_cmd: Optional[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    cells = split_into_cells(warped_gray)
    grid = np.zeros((9, 9), dtype=int)
    status = np.empty((9, 9), dtype=object)  # "blank" or "number"
    ink_ratio = np.zeros((9, 9), dtype=float)

    for i, cell in enumerate(cells):
        r, c = divmod(i, 9)
        empty, ratio = is_cell_empty(cell)
        ink_ratio[r, c] = ratio
        if empty:
            grid[r, c] = 0
            status[r, c] = "blank"
        else:
            d = read_digit(cell, tesseract_cmd)
            grid[r, c] = d
            status[r, c] = "number" if d != 0 else "blank"  # treat uncertain as blank
    return grid, status, ink_ratio


# -------------------- Main pipeline --------------------
def process_image_to_csv(
    image_path: str,
    out_grid_csv: str,
    out_cells_csv: str,
    tesseract_cmd: Optional[str] = None,
    save_warped_preview: Optional[str] = None,
) -> None:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    bgr = cv2.imread(image_path)
    if bgr is None:
        raise RuntimeError("Failed to read image (unsupported format or corrupted).")

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    quad = find_puzzle_contour(gray)
    if quad is None:
        raise RuntimeError("Sudoku contour not found. Ensure the full grid is visible and contrasted.")

    warped, _, _ = four_point_transform(bgr, quad)
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    grid, status, ink_ratio = ocr_grid(warped_gray, tesseract_cmd)

    # Export 9x9 grid (0 for blanks)
    with open(out_grid_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in range(9):
            writer.writerow(list(map(int, grid[r, :])))

    # Export per-cell detailed CSV
    with open(out_cells_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "col", "status", "value", "ink_ratio"])
        for r in range(9):
            for c in range(9):
                writer.writerow([r, c, status[r, c], int(grid[r, c]), f"{ink_ratio[r, c]:.4f}"])

    if save_warped_preview:
        cv2.imwrite(save_warped_preview, warped)

    print(f"SUCCESS: Wrote grid matrix to: {out_grid_csv}")
    print(f"SUCCESS: Wrote cell details to: {out_cells_csv}")
    if save_warped_preview:
        print(f"SUCCESS: Saved warped preview: {save_warped_preview}")


def parse_args():
    ap = argparse.ArgumentParser(
        description="Detect Sudoku digits and blanks from an image and export to CSV."
    )
    ap.add_argument("--image", required=True, help="Path to the Sudoku image (jpg/png).")
    ap.add_argument("--out-grid", default="sudoku_grid.csv", help="Output CSV path for 9x9 matrix.")
    ap.add_argument("--out-cells", default="sudoku_cells.csv", help="Output CSV path for per-cell rows.")
    ap.add_argument("--tesseract", default=None, help="Path to tesseract executable (if not on PATH).")
    ap.add_argument("--save-warped", default=None, help="Optional path to save warped grid preview (PNG).")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process_image_to_csv(
        image_path=args.image,
        out_grid_csv=args.out_grid,
        out_cells_csv=args.out_cells,
        tesseract_cmd=args.tesseract,
        save_warped_preview=args.save_warped,
    )
