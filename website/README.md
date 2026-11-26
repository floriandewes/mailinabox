# TrixieMail marketing website

Static landing page for [TrixieMail](https://github.com/quantenland-ai/trixiemail).
Content is drawn from the repository README, changelog, security guide, and setup docs.

## Preview locally

From the repository root:

```bash
# Python 3
python3 -m http.server 8080 --directory website

# or Node
npx --yes serve website -p 8080
```

Then open http://127.0.0.1:8080/

No build step is required. Edit `index.html`, `styles.css`, and `script.js` and refresh.
