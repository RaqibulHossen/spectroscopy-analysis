# Publish on GitHub

Suggested name: `spectroscopy-analysis`.

Suggested description: `Single-peak spectroscopy analysis with synthetic benchmarks, uncertainty estimates, residual diagnostics, and automated tests.`

1. Create a repository at https://github.com/new and choose public or private visibility. For the commands below, leave it empty without an initial README, license, or .gitignore.
2. Extract this archive and open a terminal inside `spectroscopy-portfolio`.
3. Run the README example and tests.
4. Replace the placeholder below with the actual clone URL GitHub provides:

```bash
git init
git add .
git commit -m "Add reproducible spectroscopy analysis prototype"
git branch -M main
git remote add origin YOUR_REPOSITORY_CLONE_URL
git push -u origin main
```

Alternatively, upload through GitHub's web interface. Include `.github/workflows/tests.yml` and `.gitignore`, and keep README.md at the repository root without an extra wrapper directory.

Suggested topics: `spectroscopy`, `python`, `scientific-computing`, `peak-fitting`, `reproducible-research`.

Check the Actions tab after publishing; the remote workflow has not yet been verified. Keep synthetic-data and AI-assistance disclosures. Select a license according to your intended reuse terms. Grant the ChatGPT GitHub integration access to the new repository for follow-up edits here.
