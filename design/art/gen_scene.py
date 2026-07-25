#!/usr/bin/env python3
"""Generates the handshake scene: an executive in profile meeting a robot.

Two figures from the waist up, facing each other, hands clasped at centre. The
jointed parts — both forearms, the robot's fingers, the human thumb — are
capsule chains, so a limb is a few points and a width ramp rather than a dozen
hand-tuned paths that drift apart on every adjustment.

The clasp is drawn once in its own coordinate space and placed with a transform,
which keeps the fingertip detail authored at a comfortable scale.

Emits an SVG fragment on stdout for pasting into design/src/index.html.
"""

import math

W, H = 1000, 720


# ---------------------------------------------------------------- primitives

def cap(p0, p1, w, fill, extra=""):
    return (f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{fill}" '
            f'stroke-width="{w:.1f}" stroke-linecap="round" fill="none"{extra}/>')


def bevel(p0, p1, w, color, opacity, side=1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1
    nx, ny = side * dy / ln, -side * dx / ln
    off = w * 0.30
    a = (p0[0] + nx * off, p0[1] + ny * off)
    b = (p1[0] + nx * off, p1[1] + ny * off)
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{color}" '
            f'stroke-width="{max(w * 0.15, 1):.1f}" stroke-linecap="round" fill="none" '
            f'opacity="{opacity}"/>')


def chain(points, widths, body, edge=None, edge_op=".5", pin=None, pin_core=None,
          side=1, extra=""):
    out = [cap(points[i], points[i + 1], widths[i], body, extra if i == 0 else "")
           for i in range(len(points) - 1)]
    if edge:
        out += [bevel(points[i], points[i + 1], widths[i], edge, edge_op, side)
                for i in range(len(points) - 1)]
    if pin:
        for i in range(1, len(points) - 1):
            x, y = points[i]
            r = widths[i] * 0.27
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" '
                       f'stroke="{pin}" stroke-width="1.6" opacity=".8"/>')
            if pin_core:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.4:.1f}" '
                           f'fill="{pin_core}" opacity=".9"/>')
    return out


# ---------------------------------------------------------------- the clasp

# Authored around (470, 260) in its own space, then transformed into the scene.
ROBOT_FINGERS = [
    ([(462, 336), (452, 312), (450, 286)], [24, 19]),
    ([(496, 336), (486, 312), (484, 283)], [25, 20]),
    ([(528, 326), (520, 304), (518, 277)], [24, 19]),
    ([(552, 310), (546, 292), (544, 268)], [21, 17]),
]
THUMB = ([(398, 228), (448, 206), (498, 196), (546, 203)], [31, 28, 23])
KNUCKLES = [(486, 218, 15), (513, 216, 16), (537, 223, 15), (556, 238, 12)]


def clasp():
    o = []
    A = o.append

    # robot palm, behind the near hand
    A('<path d="M572 224 C 524 198 478 194 458 213 C 439 230 443 269 460 289 '
      'C 481 313 540 319 572 303 Z" fill="url(#aluPalm)" stroke="var(--art-metal-lo)" '
      'stroke-width="1.6"/>')

    # back of the near hand
    A('<g filter="url(#castShadow)">')
    A('<path d="M368 236 C 406 222 444 210 484 206 C 518 203 547 211 561 226 '
      'C 576 243 571 270 554 288 C 532 308 478 320 436 318 C 410 317 392 311 400 305 Z" '
      'fill="url(#skin)"/>')
    A('</g>')
    for kx, ky, kr in KNUCKLES:
        A(f'<ellipse cx="{kx}" cy="{ky}" rx="{kr}" ry="{kr*0.78:.1f}" fill="url(#knuckle)" '
          'opacity=".85"/>')
    for x0, y0, x1, y1 in [(412, 272, 481, 229), (420, 286, 507, 229), (430, 298, 531, 235)]:
        A(f'<path d="M{x0} {y0} C {(x0+x1)/2:.0f} {(y0+y1)/2-6:.0f} {x1-14} {y1+10} {x1} {y1}" '
          'stroke="var(--art-skin-lo)" stroke-width="2.6" fill="none" opacity=".3"/>')
    A('<path d="M404 306 C 452 318 512 304 553 272" stroke="var(--art-skin-shadow)" '
      'stroke-width="16" fill="none" opacity=".26" filter="url(#soften)"/>')

    # contact shadow under each fingertip
    A('<g filter="url(#soften)" opacity=".5">')
    for pts, ws in ROBOT_FINGERS:
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        A(f'<path d="M{ax-7:.0f} {ay:.0f} L{bx-7:.0f} {by-4:.0f}" '
          f'stroke="var(--art-skin-shadow)" stroke-width="{ws[-1]+10}" '
          'stroke-linecap="round" fill="none"/>')
    A('</g>')

    for pts, ws in ROBOT_FINGERS:
        o.extend(chain(pts, ws, 'url(#aluFinger)', 'var(--art-metal-hi)', '.5',
                       pin='var(--art-metal-lo)', pin_core='var(--teal)',
                       extra=' filter="url(#fingerShadow)"'))

    A('<path d="M406 244 C 454 222 500 212 546 218" stroke="var(--art-skin-shadow)" '
      'stroke-width="13" fill="none" opacity=".32" filter="url(#soften)"/>')
    pts, ws = THUMB
    o.extend(chain(pts, ws, 'url(#skinThumb)', 'var(--art-skin-hi)', '.35',
                   extra=' filter="url(#fingerShadow)"'))
    A(f'<ellipse cx="{pts[-1][0]-4}" cy="{pts[-1][1]-3}" rx="10" ry="8" fill="url(#nail)" '
      'transform="rotate(-10 542 200)" opacity=".9"/>')
    A('<path d="M496 184 C 500 194 500 204 496 212" stroke="var(--art-skin-shadow)" '
      'stroke-width="2" fill="none" opacity=".28"/>')
    return o


# ---------------------------------------------------------------- the man

def man():
    """Executive in profile, facing right. Head ~150 units; shoulders two head-widths."""
    o = []
    A = o.append

    # --- torso, cropped by the frame. Front edge stops short of centre so the
    #     arms and the clasp have air to live in.
    A('<path d="M252 620 L249 442 C 249 384 261 346 282 328 C 297 315 316 308 334 306 '
      'L394 314 C 414 326 426 352 430 396 L432 620 Z" fill="url(#suit)"/>')
    A('<path d="M282 328 C 261 346 249 384 249 442 L252 620" stroke="var(--art-suit-hi)" '
      'stroke-width="3" fill="none" opacity=".4"/>')
    A('<path d="M330 316 C 356 330 372 358 378 392" stroke="var(--art-suit-lo)" '
      'stroke-width="3" fill="none" opacity=".45"/>')
    A('<path d="M300 312 C 322 296 352 294 376 306 C 396 316 410 336 416 358" '
      'fill="none" stroke="var(--art-suit-mid)" stroke-width="26" stroke-linecap="round"/>')
    A('<path d="M304 306 C 326 292 354 290 376 300" fill="none" '
      'stroke="var(--art-suit-hi)" stroke-width="3" opacity=".3"/>')

    # --- shirt wedge, collar points, tie
    A('<path d="M338 306 L384 318 L376 388 L346 366 Z" fill="url(#shirt)"/>')
    A('<path d="M338 306 L356 342 L334 354 Z" fill="var(--art-shirt-hi)"/>')
    A('<path d="M384 318 L370 352 L390 358 Z" fill="var(--art-shirt-lo)"/>')
    A('<path d="M356 338 L374 344 L382 368 L374 470 L356 462 L354 368 Z" fill="url(#tie)"/>')
    A('<path d="M356 338 L374 344 L372 358 L354 352 Z" fill="var(--art-tie-hi)" opacity=".5"/>')

    # --- lapels
    A('<path d="M384 318 C 404 334 414 368 412 410 L376 388 Z" fill="url(#lapel)"/>')
    A('<path d="M338 306 C 320 326 312 362 314 400 L346 366 Z" fill="url(#lapel)" opacity=".75"/>')

    # --- neck: short, and set into the collar
    A(cap((334, 244), (340, 300), 76, 'url(#skinDim)'))
    A('<path d="M314 272 C 332 290 352 296 368 294" stroke="var(--art-skin-shadow)" '
      'stroke-width="12" fill="none" opacity=".34" filter="url(#soften)"/>')

    # --- head in profile, facing right
    A('<g filter="url(#castShadow)">')
    A('<path d="M312 112 C 354 108 380 128 386 160 C 388 172 384 176 386 182 '
      'C 390 190 404 198 403 205 C 402 212 390 210 388 216 C 386 222 392 226 390 232 '
      'C 388 238 380 236 380 242 C 380 250 386 254 382 258 C 374 266 352 272 338 270 '
      'C 314 266 294 250 286 226 C 276 196 274 152 290 130 C 296 120 302 114 312 112 Z" '
      'fill="url(#skin)"/>')
    A('</g>')
    A('<path d="M358 158 C 368 154 378 156 383 162" stroke="var(--art-skin-shadow)" '
      'stroke-width="6" fill="none" opacity=".45" stroke-linecap="round"/>')
    A('<path d="M364 170 C 372 166 380 168 384 173" stroke="var(--art-eye)" '
      'stroke-width="4.5" fill="none" opacity=".85" stroke-linecap="round"/>')
    A('<path d="M372 214 C 380 212 386 213 390 216" stroke="var(--art-skin-shadow)" '
      'stroke-width="3.4" fill="none" opacity=".55" stroke-linecap="round"/>')
    A('<path d="M350 232 C 358 246 368 252 378 252" stroke="var(--art-skin-shadow)" '
      'stroke-width="7" fill="none" opacity=".22" filter="url(#soften)"/>')
    A('<path d="M322 180 C 332 177 339 186 337 198 C 335 210 328 215 322 212 '
      'C 316 208 315 186 322 180 Z" fill="url(#skinDim)" stroke="var(--art-skin-shadow)" '
      'stroke-width="1.4" opacity=".95"/>')
    A('<path d="M326 188 C 332 190 332 202 326 206" stroke="var(--art-skin-shadow)" '
      'stroke-width="2" fill="none" opacity=".5"/>')
    A('<path d="M376 134 C 366 112 334 100 308 106 C 284 112 270 136 268 168 '
      'C 267 190 272 210 280 226 C 274 192 280 158 294 144 C 310 128 350 128 376 134 Z" '
      'fill="url(#hair)"/>')
    A('<path d="M294 142 C 308 126 346 124 372 130" stroke="var(--art-hair-hi)" '
      'stroke-width="2.4" fill="none" opacity=".45"/>')

    # --- near arm reaching to the clasp
    A('<ellipse cx="412" cy="360" rx="42" ry="38" fill="url(#suitArm)"/>')
    o.extend(chain([(412, 362), (452, 448), (486, 486)], [54, 38],
                   'url(#suitArm)', 'var(--art-suit-hi)', '.35', side=-1))
    A('<path d="M388 334 C 412 344 426 362 432 386" stroke="var(--art-suit-hi)" '
      'stroke-width="2.6" fill="none" opacity=".35"/>')
    A(cap((478, 478), (492, 491), 29, 'url(#shirt)'))
    return o


# ---------------------------------------------------------------- the robot

def robot():
    """Humanoid unit in profile, facing left. Angular, matte, one warm indicator."""
    o = []
    A = o.append

    # --- torso shell, front edge held back from centre
    A('<path d="M792 620 L795 442 C 795 384 783 346 762 328 C 747 315 728 308 710 306 '
      'L650 314 C 630 326 618 352 614 396 L612 620 Z" fill="url(#aluBody)"/>')
    A('<path d="M650 314 C 630 326 618 352 614 396 L612 620" '
      'stroke="var(--art-metal-hi)" stroke-width="2.6" fill="none" opacity=".4"/>')
    A('<path d="M742 314 C 720 298 690 296 666 308 C 646 318 630 340 624 362" '
      'fill="none" stroke="var(--art-metal-lo)" stroke-width="28" stroke-linecap="round"/>')
    A('<path d="M738 308 C 716 294 688 292 666 302" fill="none" '
      'stroke="var(--art-metal-hi)" stroke-width="3" opacity=".35"/>')
    for d, op in [("M622 396 C 664 384 714 388 752 408", ".7"),
                  ("M616 472 C 660 458 714 462 762 484", ".55"),
                  ("M612 564 C 658 550 716 554 768 576", ".4")]:
        A(f'<path d="{d}" stroke="var(--art-metal-deep)" stroke-width="4" fill="none" opacity="{op}"/>')
    A('<circle cx="640" cy="424" r="16" fill="var(--art-metal-deep)"/>')
    A('<circle cx="640" cy="424" r="9" fill="var(--teal)" opacity=".9"/>')
    A('<circle cx="640" cy="424" r="16" fill="none" stroke="var(--art-metal-hi)" '
      'stroke-width="1.6" opacity=".55"/>')

    # --- neck: short stacked actuator
    A(cap((692, 248), (690, 304), 54, 'var(--art-metal-lo)'))
    for y in (266, 282, 298):
        A(f'<path d="M664 {y} L716 {y-2}" stroke="var(--art-metal-deep)" stroke-width="3.2" '
          'opacity=".8"/>')

    # --- head: an angular helmet in profile, facing left
    A('<g filter="url(#castShadow)">')
    A('<path d="M622 186 C 622 146 646 118 686 114 C 726 110 754 132 758 170 '
      'C 762 202 756 234 744 252 C 730 272 698 278 670 270 C 640 262 622 236 622 208 Z" '
      'fill="url(#aluHead)"/>')
    A('</g>')
    # chamfered brow line and crown split
    A('<path d="M624 182 C 656 158 712 154 756 172" stroke="var(--art-metal-deep)" '
      'stroke-width="3.6" fill="none" opacity=".75"/>')
    A('<path d="M626 173 C 658 150 714 146 756 163" stroke="var(--art-metal-hi)" '
      'stroke-width="1.8" fill="none" opacity=".5"/>')
    # visor
    A('<path d="M620 200 C 646 187 690 185 718 194 L716 220 C 688 210 648 212 622 224 Z" '
      'fill="var(--art-visor)"/>')
    A('<path d="M623 205 C 649 192 688 190 715 198" stroke="var(--teal)" '
      'stroke-width="4.5" fill="none" opacity=".95"/>')
    A('<path d="M623 205 C 649 192 688 190 715 198" stroke="var(--teal)" '
      'stroke-width="13" fill="none" opacity=".2" filter="url(#soften)"/>')
    # mandible plate and vents
    A('<path d="M638 242 C 666 256 700 258 730 248 L724 266 C 696 278 662 276 640 260 Z" '
      'fill="var(--art-metal-lo)"/>')
    for x in (694, 708, 722):
        A(f'<path d="M{x} 232 L{x+6} 250" stroke="var(--art-metal-deep)" stroke-width="2.6" '
          'opacity=".65"/>')
    A('<circle cx="730" cy="214" r="16" fill="var(--art-metal-lo)" '
      'stroke="var(--art-metal-hi)" stroke-width="1.6" opacity=".95"/>')
    A('<circle cx="730" cy="214" r="6" fill="var(--art-metal-deep)"/>')
    A('<path d="M634 156 C 654 128 684 118 706 117" stroke="var(--art-metal-hi)" '
      'stroke-width="3" fill="none" opacity=".5"/>')

    # --- near arm reaching to the clasp
    A('<ellipse cx="618" cy="362" rx="44" ry="39" fill="url(#aluJoint)" '
      'stroke="var(--art-metal-deep)" stroke-width="2"/>')
    A('<circle cx="618" cy="362" r="15" fill="var(--art-metal-deep)"/>')
    A('<circle cx="618" cy="362" r="7" fill="var(--teal)" opacity=".8"/>')
    o.extend(chain([(618, 366), (580, 452), (546, 490)], [50, 38],
                   'url(#aluArm)', 'var(--art-metal-hi)', '.45',
                   pin='var(--art-metal-deep)', side=1))
    A('<path d="M598 398 C 580 440 564 472 550 494" stroke="var(--art-cable)" '
      'stroke-width="6" fill="none" stroke-linecap="round" opacity=".8"/>')
    A('<path d="M598 398 C 580 440 564 472 550 494" stroke="var(--teal)" '
      'stroke-width="1.6" fill="none" stroke-linecap="round" opacity=".45"/>')
    return o


# ---------------------------------------------------------------- assembly

def build():
    o = []
    A = o.append

    A('<g filter="url(#soften)" opacity=".45">')
    A('<ellipse cx="512" cy="572" rx="196" ry="40" fill="var(--art-shadow)"/>')
    A('</g>')

    o.extend(robot())
    o.extend(man())

    # the clasp, authored around (470,260), placed at the meeting point
    A('<g transform="translate(514 496) rotate(21) scale(0.62) translate(-470 -262)">')
    o.extend(clasp())
    A('</g>')

    return "\n          ".join(o)


DEFS = """
            <radialGradient id="skin" cx="0.42" cy="0.3" r="0.85">
              <stop offset="0" stop-color="var(--art-skin-hi)"/>
              <stop offset=".45" stop-color="var(--art-skin-mid)"/>
              <stop offset="1" stop-color="var(--art-skin-lo)"/>
            </radialGradient>
            <linearGradient id="skinDim" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stop-color="var(--art-skin-lo)"/>
              <stop offset="1" stop-color="var(--art-skin-mid)"/>
            </linearGradient>
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
            <linearGradient id="hair" x1="0" y1="0" x2="0.4" y2="1">
              <stop offset="0" stop-color="var(--art-hair-hi)"/>
              <stop offset="1" stop-color="var(--art-hair-lo)"/>
            </linearGradient>

            <linearGradient id="suit" x1="0" y1="0" x2="1" y2="0.4">
              <stop offset="0" stop-color="var(--art-suit-lo)"/>
              <stop offset=".55" stop-color="var(--art-suit-mid)"/>
              <stop offset="1" stop-color="var(--art-suit-lo)"/>
            </linearGradient>
            <linearGradient id="suitArm" x1="0" y1="0" x2="0.3" y2="1">
              <stop offset="0" stop-color="var(--art-suit-mid)"/>
              <stop offset="1" stop-color="var(--art-suit-lo)"/>
            </linearGradient>
            <linearGradient id="lapel" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="var(--art-suit-hi)" stop-opacity=".55"/>
              <stop offset="1" stop-color="var(--art-suit-mid)"/>
            </linearGradient>
            <linearGradient id="shirt" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stop-color="var(--art-shirt-lo)"/>
              <stop offset="1" stop-color="var(--art-shirt-hi)"/>
            </linearGradient>
            <linearGradient id="tie" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stop-color="var(--art-tie-lo)"/>
              <stop offset="1" stop-color="var(--art-tie-hi)"/>
            </linearGradient>

            <linearGradient id="aluBody" x1="0" y1="0" x2="0.9" y2="0.3">
              <stop offset="0" stop-color="var(--art-metal-mid)"/>
              <stop offset=".45" stop-color="var(--art-metal-lo)"/>
              <stop offset="1" stop-color="var(--art-metal-deep)"/>
            </linearGradient>
            <linearGradient id="aluHead" x1="0" y1="0" x2="0.7" y2="1">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset=".4" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </linearGradient>
            <linearGradient id="aluArm" x1="0" y1="0" x2="0.2" y2="1">
              <stop offset="0" stop-color="var(--art-metal-mid)"/>
              <stop offset=".4" stop-color="var(--art-metal-lo)"/>
              <stop offset="1" stop-color="var(--art-metal-deep)"/>
            </linearGradient>
            <linearGradient id="aluFinger" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset=".42" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </linearGradient>
            <radialGradient id="aluPalm" cx="0.65" cy="0.3" r="0.8">
              <stop offset="0" stop-color="var(--art-metal-mid)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </radialGradient>
            <radialGradient id="aluJoint" cx="0.35" cy="0.3" r="0.8">
              <stop offset="0" stop-color="var(--art-metal-hi)"/>
              <stop offset="1" stop-color="var(--art-metal-lo)"/>
            </radialGradient>

            <filter id="soften" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="7"/>
            </filter>
            <filter id="castShadow" x="-25%" y="-25%" width="160%" height="160%">
              <feDropShadow dx="7" dy="11" stdDeviation="11" flood-color="var(--art-shadow)"
                            flood-opacity=".4"/>
            </filter>
            <filter id="fingerShadow" x="-40%" y="-40%" width="190%" height="190%">
              <feDropShadow dx="-3" dy="4" stdDeviation="3.5" flood-color="var(--art-shadow)"
                            flood-opacity=".42"/>
            </filter>
"""

if __name__ == "__main__":
    print("<defs>" + DEFS + "          </defs>")
    print("          " + build())
