# Profile implementation

This package is ready for review, not deployed. It implements the approved white / ink / blue / mustard design as linked SVG sections rather than a single screenshot.

## Installation

Create the public repository `jichuo1/jichuo1` after approving publication. Copy README.md, assets/, scripts/, tests/, data/, source.json, contributions-source.html and .github/ into it. Commit to its default branch. GitHub displays the root README on the account profile. The workflow will run manually or twice daily after publication; no new personal access token is needed. It uses GitHub's ephemeral job token with contents:write limited to this repository.

The supplied schedule is 00:23 and 12:23 UTC. GitHub may delay scheduled jobs, and inactive public repositories may have scheduled workflows disabled. The page shows the last successful check time rather than claiming live data. No workflow has been activated here.

## Data definitions

- Stars and forks: sums across all public repositories owned by this account, including fork repositories. Repositories: all public owned repositories; private repositories are excluded. A new profile repository will naturally increase the repository count after the first update.
- Downloads: all public Release asset download counters in the four featured projects, including prerelease assets. These are not users, unique downloads, source archive downloads or Actions artifacts.
- Project version: most recently published non-draft, non-prerelease Release. A Canary is never promoted to stable.
- Languages: number of public repositories by their GitHub primary language, not code bytes, coding time or proficiency. Unknown languages are Other.
- Contribution calendar: public HTML from GitHub's own contributions endpoint. It shows GitHub's daily intensity levels, not an invented count. Private activity may be anonymized by the owner's GitHub display settings. This HTML is not a versioned API; parser failure intentionally prevents publishing a new snapshot. No private repository names or credentials are used.

## Local commands

Python 3.10+ standard library only:

    python3 -m unittest discover -s tests -v
    python3 scripts/build.py --source source.json --calendar contributions-source.html
    python3 scripts/build.py

The last command fetches current public data. An optional existing GITHUB_TOKEN is read from the process environment and used only for api.github.com, never saved. No additional credential is required for the public contribution page. Without a token the GitHub REST anonymous rate limit may be exhausted; failure leaves generated files unchanged during acquisition/validation.

All data is fetched and validated before rendering and staging. Every output file is atomically replaced; the workflow pushes the complete output as one Git commit. The multi-file local replace is not a filesystem-wide transaction, but partial local results will not be pushed after a step fails. Push races fail rather than force-pushing. There is no pull_request trigger and no execution of untrusted repository content from other projects.

## Appearance and accessibility

README uses picture sources for dark and light themes and screens up to 600 px. Mobile has a two-by-two stats layout, stacked project details, and the same calendar split into chronological panels. Project images are links to their repositories; calendar links to the account overview. SVGs have titles and the README has alt text. SVG font fallback is Georgia / Times New Roman / serif, requiring no font download or font redistribution.

`preview.html` is a local rendering helper, not a custom GitHub website. GitHub may add default README spacing, image scaling, and caching. Verify the actual hosted profile after deployment. Do not promise hover animations, custom CSS or JavaScript on the GitHub page.

## Validation performed

- 21 standard-library tests passed, including pagination, private filtering, duplicate rejection, stable vs prerelease selection, draft exclusion, malformed calendar failure, XML escaping, source fixture consistency and desktop/mobile SVG parsing.
- Actual public repository metadata and all four complete Release lists were retrieved with the existing read-only GitHub connector at 2026-10-22 13:40 UTC. Public calendar HTML was retrieved separately. The current snapshot has 159 Stars, 7 public repos, 11 Forks and 3,713 asset downloads.
- SVG assets were rendered and visually inspected locally with Inkscape. These preview PNGs are code-generated renders, not GPT Image mocks.
- Browser rendering was attempted but blocked by the cloud process sandbox; the headless browser could not start. This is not a successful browser or hosted GitHub validation.
- No remote repository was created or modified; no Actions run, publication, recurring credential or subscription was configured.

## Sources

- https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://api.github.com/users/jichuo1/repos
- https://github.com/users/jichuo1/contributions
- Each featured repository's public `/releases` REST collection.
