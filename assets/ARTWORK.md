
## Natural scene motion and lettering
Project scenes use distinct CSS cycles: a hopping robot chasing a star, three independent firefly loops, a true semicircular sunrise-to-sunset orbit with hidden reset, and a token emission arc with a settling bounce. Reduced-motion disables all cycles and keeps meaningful still frames. Titles and numeric displays use original 5×7 vector glyphs; the motto retains serif italic and explanatory copy uses monospace. No remote fonts or script execution are required.

The README now embeds one composite poster SVG per theme/breakpoint so the paper, all panels and corner share one animation clock. A subtle 2D skew and moving shadow suggest wind-driven perspective; this is not a true 3D mesh deformation. Individual repository links are retained as a compact link row below the image because links inside an SVG image are not interactive in GitHub README rendering. Original glyph shapes preserve accessible title/aria labels; tiny copy remains monospace.

## Gusts, refined drawings and introduction
Wind now combines a 7.1-second uneven gust sequence with a 2.31-second flutter cycle, larger safe padding, stronger corner lift and damping. These deterministic cycles look irregular; they are not random weather simulation. Robot anticipation/landing and sampled parabolic token flight replace uniform motion. Fireflies follow sampled elliptical paths; glass, faceplate, veins, rim and terminal details are refined.

Except for the motto, authored text rolls once on SVG load: vector title/numeric columns have differing easing and high-to-low-place settling times; small explanatory lines roll as units with distinct timing to preserve readability. Accessible labels always contain final data. Reduced-motion shows final content immediately. Reload/image-cache behavior is controlled by GitHub/browser, so an animation is not guaranteed to restart on every SPA navigation.

Each non-text decoration now has a one-shot entrance wrapper independent of its loop: project mascots fly in, rise or settle; language bars grow from the left; calendar cells populate in a staggered wave; rules and Star meters expand. Reduced-motion bypasses these entrances. The motto stays stationary. Calendar values remain the fetched snapshot, not simulated activity.

Whole-poster gust and flutter transforms are now disabled. README wind is restricted to the lower-right corner; the interactive homepage has the richer spatially attenuated spring model. The interactive static source is in site/, with a Pages workflow. Its GitHub entry is changed only after a verified successful deployment.
