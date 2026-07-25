#!/usr/bin/env python3
"""Generates the handshake illustration.

The drawing is parametric because the parts that carry the realism — the four
robot fingers and the two thumb segments — are capsule chains whose widths taper
along the chain. Writing them by hand meant fifty near-identical path elements
that drifted out of alignment on every tweak; here a chain is four points and a
width ramp, and the bevel highlight is derived from the same curve.

Emits an SVG fragment on stdout for pasting into design/src/index.html.
"""

import math

# ---------------------------------------------------------------- helpers

def cap(p0, p1, w, fill, extra=""):
    """A capsule: round-capped stroke between two points."""
    return (f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" '
            f'stroke="{fill}" stroke-width="{w:.1f}" stroke-linecap="round" fill="none"{extra}/>')


def bevel(p0, p1, w, color, opacity):
    """Thin highlight riding the upper edge of a capsule — reads as a machined bevel."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1
    nx, ny = dy / ln, -dx / ln          # normal, pointing "up" for our left-to-right chains
    off = w * 0.30
    a = (p0[0] + nx * off, p0[1] + ny * off)
    b = (p1[0] + nx * off, p1[1] + ny * off)
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{color}" '
            f'stroke-width="{w * 0.16:.1f}" stroke-linecap="round" fill="none" opacity="{opacity}"/>')


def chain(points, widths, body, edge, edge_op=".55", pin=None, pin_core=None, shadow=""):
    """A jointed limb: capsules between consecutive points, pins at the interior joints."""
    out = []
    for i in range(len(points) - 1):
        out.append(cap(points[i], points[i + 1], widths[i], body, shadow if i == 0 else ""))
    for i in range(len(points) - 1):
        out.append(bevel(points[i], points[i + 1], widths[i], edge, edge_op))
    if pin:
        for i in range(1, len(points) - 1):
            x, y = points[i]
            r = widths[i] * 0.26
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" '
                       f'stroke="{pin}" stroke-width="1.4" opacity=".75"/>')
            if pin_core:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.42:.1f}" fill="{pin_core}" opacity=".9"/>')
    return out


# ---------------------------------------------------------------- geometry

# The robot grips from the far side, so only the last two phalanges of each
# finger clear the near hand's lower edge and press onto its back. Left to right.
ROBOT_FINGERS = [
    ([(462, 336), (452, 312), (450, 286)], [24, 19]),
    ([(496, 336), (486, 312), (484, 283)], [25, 20]),
    ([(528, 326), (520, 304), (518, 277)], [24, 19]),
    ([(552, 310), (546, 292), (544, 268)], [21, 17]),
]

# The human thumb wrapping over the top of the robot's hand.
THUMB = ([(398, 228), (448, 206), (498, 196), (546, 203)], [31, 28, 23])

# Knuckle bumps along the top-right edge of the back of the hand.
KNUCKLES = [(486, 218, 15), (513, 216, 16), (537, 223, 15), (556, 238, 12)]


def build():
    o = []
    A = o.append

    # The backdrop and key light live on the panel in CSS, not here: the drawing
    # letterboxes inside a taller panel, and a rect painted in here would end at
    # the viewBox edge and leave a visible seam.

    # ---- robot forearm, behind everything
    A('<g filter="url(#castShadow)">')
    A('<path d="M942 366 L606 242 L578 308 L900 452 Z" fill="url(#aluArm)"/>')
    A('</g>')
    A('<path d="M942 366 L606 242" stroke="url(#aluEdge)" stroke-width="2.6" fill="none" opacity=".85"/>')
    A('<path d="M900 452 L578 308" stroke="var(--art-metal-deep)" stroke-width="3" fill="none" opacity=".7"/>')
    # forearm plate seams
    for x0, y0, x1, y1 in [(726, 298, 754, 233), (830, 344, 858, 278)]:
        A(f'<path d="M{x0} {y0} L{x1} {y1}" stroke="var(--art-metal-deep)" stroke-width="3" opacity=".8"/>')
        A(f'<path d="M{x0+5} {y0} L{x1+5} {y1}" stroke="var(--art-metal-hi)" stroke-width="1.2" opacity=".35"/>')
    # cable bundle along the underside
    A('<path d="M892 440 C 806 396 706 348 604 300" stroke="var(--art-cable)" stroke-width="7" '
      'fill="none" stroke-linecap="round" opacity=".8"/>')
    A('<path d="M892 440 C 806 396 706 348 604 300" stroke="var(--teal)" stroke-width="1.6" '
      'fill="none" stroke-linecap="round" opacity=".5"/>')

    # ---- wrist joint
    A('<circle cx="583" cy="270" r="30" fill="url(#jointG)" stroke="var(--art-metal-lo)" stroke-width="2"/>')
    A('<circle cx="583" cy="270" r="30" fill="none" stroke="var(--art-metal-hi)" stroke-width="1.2" opacity=".5"/>')
    A('<circle cx="583" cy="270" r="12" fill="var(--teal)" opacity=".85"/>')
    A('<circle cx="583" cy="270" r="12" fill="none" stroke="var(--art-metal-hi)" stroke-width="1.2" opacity=".6"/>')
    A('<circle cx="583" cy="270" r="20" fill="none" stroke="var(--teal)" stroke-width="1.2" opacity=".35"/>')

    # ---- robot palm plate, mostly hidden behind the human hand
    A('<path d="M572 224 C 524 198 478 194 458 213 C 439 230 443 269 460 289 '
      'C 481 313 540 319 572 303 Z" fill="url(#aluPalm)" stroke="var(--art-metal-lo)" stroke-width="1.6"/>')

    # ---- human forearm: suit sleeve, cuff, then the hand
    A('<g filter="url(#castShadow)">')
    A('<path d="M-42 375 L334 231 L370 317 L2 482 Z" fill="url(#suit)"/>')
    A('</g>')
    A('<path d="M-42 375 L334 231" stroke="var(--art-suit-hi)" stroke-width="2.2" fill="none" opacity=".6"/>')
    # a fold in the fabric
    A('<path d="M120 320 C 190 292 250 270 300 250" stroke="var(--art-suit-lo)" stroke-width="6" '
      'fill="none" opacity=".35"/>')
    # shirt cuff
    A('<path d="M334 231 L370 217 L404 302 L370 317 Z" fill="url(#shirt)"/>')
    A('<path d="M352 224 L387 309" stroke="var(--art-shirt-lo)" stroke-width="1.6" opacity=".8"/>')
    A('<circle cx="380" cy="286" r="5.5" fill="var(--art-shirt-lo)"/>')
    A('<circle cx="378.5" cy="284.5" r="2" fill="var(--art-shirt-hi)" opacity=".8"/>')

    # ---- back of the hand
    A('<g filter="url(#castShadow)">')
    A('<path d="M368 236 C 406 222 444 210 484 206 C 518 203 547 211 561 226 '
      'C 576 243 571 270 554 288 C 532 308 478 320 436 318 C 410 317 392 311 400 305 Z" '
      'fill="url(#skin)"/>')
    A('</g>')
    # knuckles
    for kx, ky, kr in KNUCKLES:
        A(f'<ellipse cx="{kx}" cy="{ky}" rx="{kr}" ry="{kr*0.78:.1f}" fill="url(#knuckle)" opacity=".85"/>')
    # tendons running to the knuckles
    for x0, y0, x1, y1 in [(412, 272, 481, 229), (420, 286, 507, 229), (430, 298, 531, 235)]:
        A(f'<path d="M{x0} {y0} C {(x0+x1)/2:.0f} {(y0+y1)/2 - 6:.0f} {x1-14} {y1+10} {x1} {y1}" '
          'stroke="var(--art-skin-lo)" stroke-width="2.4" fill="none" opacity=".28"/>')
    # form shadow along the lower edge of the hand
    A('<path d="M404 306 C 452 318 512 304 553 272" stroke="var(--art-skin-shadow)" '
      'stroke-width="16" fill="none" opacity=".26" filter="url(#soften)"/>')

    # ---- occlusion where the robot fingers press into the hand
    A('<g filter="url(#soften)" opacity=".5">')
    for pts, ws in ROBOT_FINGERS:
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        A(f'<path d="M{ax - 7:.0f} {ay:.0f} L{bx - 7:.0f} {by - 4:.0f}" '
          f'stroke="var(--art-skin-shadow)" stroke-width="{ws[-1] + 10}" '
          'stroke-linecap="round" fill="none"/>')
    A('</g>')

    # ---- robot fingers
    for pts, ws in ROBOT_FINGERS:
        o.extend(chain(pts, ws, 'url(#aluFinger)', 'var(--art-metal-hi)', '.5',
                       pin='var(--art-metal-lo)', pin_core='var(--teal)',
                       shadow=' filter="url(#fingerShadow)"'))

    # ---- human thumb, laid over the robot's hand
    pts, ws = THUMB
    o.extend(chain(pts, ws, 'url(#skinThumb)', 'var(--art-skin-hi)', '.35',
                   shadow=' filter="url(#fingerShadow)"'))
    # thumbnail
    A(f'<ellipse cx="{pts[-1][0]-4}" cy="{pts[-1][1]-3}" rx="10" ry="8" fill="url(#nail)" '
      'transform="rotate(-10 542 200)" opacity=".9"/>')
    A('<path d="M406 244 C 454 222 500 212 546 218" stroke="var(--art-skin-shadow)" '
      'stroke-width="13" fill="none" opacity=".32" filter="url(#soften)"/>')
    # crease between the thumb segments
    A('<path d="M496 184 C 500 194 500 204 496 212" stroke="var(--art-skin-shadow)" '
      'stroke-width="2" fill="none" opacity=".28"/>')

    return "\n          ".join(o)


DEFS = """
            <linearGradient id="suit" x1="0" y1="1" x2="0.7" y2="0">
              <stop offset="0" stop-color="var(--art-suit-lo)"/>
              <stop offset=".55" stop-color="var(--art-suit-mid)"/>
              <stop offset="1" stop-color="var(--art-suit-hi)"/>
            </linearGradient>
            <linearGradient id="shirt" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stop-color="var(--art-shirt-lo)"/>
              <stop offset="1" stop-color="var(--art-shirt-hi)"/>
            </linearGradient>

            <radialGradient id="skin" cx="0.42" cy="0.3" r="0.85">
              <stop offset="0" stop-color="var(--art-skin-hi)"/>
              <stop offset=".45" stop-color="var(--art-skin-mid)"/>
              <stop offset="1" stop-color="var(--art-skin-lo)"/>
            </radialGradient>
            <radialGradient id="knuckle" cx="0.38" cy="0.32" r="0.7">
              <stop offset="0" stop-color="var(--art-skin-hi)"/>
              <stop offset="1" stop-color="var(--art-skin-mid)" stop-opacity="0"/>
            </radialGradient>
            <linearGradient id="skinThumb" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="var(--art-skin-hi)"/>
              <stop offset=".5" stop-color="var(--art-skin-mid)"/>
              <stop offset="1" stop-color="var(--art-skin-lo)"/>
            </linearGradient>
            <linearGradient id="nail" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="var(--art-nail-hi)"/>
              <stop offset="1" stop-color="var(--art-nail-lo)"/>
            </linearGradient>

            <linearGradient id="aluArm" x1="0" y1="0" x2="0.15" y2="1">
              <stop offset="0" stop-color="var(--art-metal-mid)"/>
              <stop offset=".28" stop-color="var(--art-metal-lo)"/>
              <stop offset="1" stop-color="var(--art-metal-deep)"/>
            </linearGradient>
            <linearGradient id="alu" x1="0" y1="0" x2="0.2" y2="1">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset=".38" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </linearGradient>
            <linearGradient id="aluEdge" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stop-color="var(--art-metal-hi)" stop-opacity=".2"/>
              <stop offset=".5" stop-color="var(--art-metal-hi)"/>
              <stop offset="1" stop-color="var(--art-metal-hi)" stop-opacity=".3"/>
            </linearGradient>
            <radialGradient id="aluPalm" cx="0.65" cy="0.3" r="0.8">
              <stop offset="0" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </radialGradient>
            <linearGradient id="aluFinger" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset=".42" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </linearGradient>
            <radialGradient id="jointG" cx="0.35" cy="0.3" r="0.8">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </radialGradient>

            <filter id="soften" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="7"/>
            </filter>
            <filter id="castShadow" x="-20%" y="-20%" width="150%" height="150%">
              <feDropShadow dx="6" dy="10" stdDeviation="10" flood-color="var(--art-shadow)" flood-opacity=".45"/>
            </filter>
            <filter id="fingerShadow" x="-40%" y="-40%" width="190%" height="190%">
              <feDropShadow dx="-3" dy="4" stdDeviation="3.5" flood-color="var(--art-shadow)" flood-opacity=".42"/>
            </filter>
"""

if __name__ == "__main__":
    print("<defs>" + DEFS + "          </defs>")
    print("          " + build())
