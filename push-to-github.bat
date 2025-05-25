@echo off
echo Preparing to push Frizerie to GitHub...

:: Initialize git repository if not already initialized
if not exist .git (
  echo Initializing git repository...
  git init
) else (
  echo Git repository already initialized.
)

:: Add the remote
echo Setting up remote repository...
git remote remove origin
git remote add origin https://github.com/alexandruarmas/Frizerie.git

:: Add all files
echo Adding files to git...
git add .

:: Commit changes
echo Committing changes...
git commit -m "Initial commit with complete Frizerie project"

:: Push to GitHub
echo Pushing to GitHub...
git push -u origin main

echo Done! Your project is now on GitHub.
echo Next, you can deploy to Vercel by following the instructions in VERCEL-DEPLOYMENT.md
pause 