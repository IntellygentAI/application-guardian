# Accessibility

Default target: WCAG 2.2 Level AA for web interfaces. For native mobile apps, apply the platform accessibility guidance that matches that bar: labelled controls, dynamic type, screen-reader order, and touch targets.

Test:

- Text enlarged to 200% and reflow at narrow viewport widths.
- System accessibility font settings.
- Dark mode, light mode, and switching theme during active use.
- High-contrast settings and reduced-motion preferences.
- Keyboard-only navigation, visible focus, and logical tab order.
- Screen readers, accessible form labels, and accessible error messages.
- Modal focus management: focus moves in, stays trapped while open, and returns on close.
- Colour contrast and touch target size.
- Alternative text for meaningful images. Decorative images are hidden from assistive tech.

Essential functionality must remain available without relying only on colour, gestures, sound, hover, or visual position.

Use the repository's existing accessibility tools, such as axe-core, when they are already present. Do not add a new accessibility stack only to satisfy this skill. Record automated results separately from manual keyboard and screen-reader checks. Automated scans do not prove WCAG conformance.

Record each check as PASS, FAIL, NOT TESTED, BLOCKED, or NOT APPLICABLE, with the viewport, browser, and assistive technology used.
