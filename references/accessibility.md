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

For the three checks that public pages most often miss, use the WCAG 2.2 criteria by name:

- [1.1.1 Non-text Content](https://www.w3.org/TR/WCAG22/#non-text-content): a meaningful image has a text alternative that serves the same purpose. A decorative image is hidden from assistive technology. A filename or the word "image" is not an alternative.
- [1.4.3 Contrast (Minimum)](https://www.w3.org/TR/WCAG22/#contrast-minimum): ordinary text is at least 4.5:1 against its background. Large text, 18pt or 14pt bold, is at least 3:1. Logotypes and disabled controls are the stated exceptions. [1.4.11](https://www.w3.org/TR/WCAG22/#non-text-contrast) asks 3:1 for meaningful graphics and interface components.
- [2.1.1 Keyboard](https://www.w3.org/TR/WCAG22/#keyboard): every function that a pointer can operate can be operated from the keyboard, except a function that cannot be performed from a keyboard. Focus is visible ([2.4.7](https://www.w3.org/TR/WCAG22/#focus-visible)). A control that exists only as a click handler on a `div` is a failure.

Use the repository's existing accessibility tools, such as axe-core, when they are already present. Do not add a new accessibility stack only to satisfy this skill. Record automated results separately from manual keyboard and screen-reader checks. Automated scans do not prove WCAG conformance.

Record each check as PASS, FAIL, NOT TESTED, BLOCKED, or NOT APPLICABLE, with the viewport, browser, and assistive technology used.
