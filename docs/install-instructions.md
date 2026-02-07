# Install Instructions

This guide replaces the old `docs/install/` folder. It shows how to clone the repo and sync skills into your local skills folder without deleting your existing custom skills.

## Quick Start (Project-Local)

Run from your project root. This pulls the skills into `./skills` without leaving a clone behind.

### macOS / Linux

```bash
tmpdir="$(mktemp -d)" && git clone https://github.com/Ariel-Rodriguez/programming-skills.git "$tmpdir" && mkdir -p ./skills && rsync -a --exclude ".git" --exclude ".DS_Store" "$tmpdir/skills/" ./skills/ && rm -rf "$tmpdir"
```

### Windows (PowerShell)

```powershell
$tmp = New-Item -ItemType Directory -Force -Path ([IO.Path]::Combine($env:TEMP, "programming-skills-" + [Guid]::NewGuid().ToString())); git clone https://github.com/Ariel-Rodriguez/programming-skills.git $tmp.FullName; mkdir .\\skills -Force; robocopy (Join-Path $tmp.FullName "skills") (Join-Path (Get-Location) "skills") /E /XO; Remove-Item -Recurse -Force $tmp.FullName
```

## 1) Clone the Repo (HTTP)

### macOS / Linux

```bash
git clone https://github.com/Ariel-Rodriguez/programming-skills.git
cd programming-skills
```

### Windows (PowerShell)

```powershell
git clone https://github.com/Ariel-Rodriguez/programming-skills.git
cd programming-skills
```

## One-Line Install (Clone + Sync + Cleanup)

Use these if you just want to pull skills into your local folder and remove the temporary clone afterward.

### macOS / Linux (single command, sync into current project)

```bash
tmpdir="$(mktemp -d)" && git clone https://github.com/Ariel-Rodriguez/programming-skills.git "$tmpdir" && mkdir -p ./skills && rsync -a --exclude ".git" --exclude ".DS_Store" "$tmpdir/skills/" ./skills/ && rm -rf "$tmpdir"
```

### Windows (PowerShell single command, sync into current project)

```powershell
$tmp = New-Item -ItemType Directory -Force -Path ([IO.Path]::Combine($env:TEMP, "programming-skills-" + [Guid]::NewGuid().ToString())); git clone https://github.com/Ariel-Rodriguez/programming-skills.git $tmp.FullName; mkdir .\\skills -Force; robocopy (Join-Path $tmp.FullName "skills") (Join-Path (Get-Location) "skills") /E /XO; Remove-Item -Recurse -Force $tmp.FullName
```

## 2) Sync Skills to Your Project Folder (Recommended)

Default destination is the current project’s `./skills/` folder.

If you are already inside the cloned repo, the `skills/` folder is already present and no extra sync is required.

If you want to copy skills into a different project, run these from the **cloned repo** and set a destination path.

### macOS / Linux (rsync)

```bash
DEST=/path/to/your/project/skills
mkdir -p "$DEST"
rsync -a --exclude ".git" --exclude ".DS_Store" skills/ "$DEST/"
```

This merges new skills and updates existing ones, without removing your own custom folders.

### Windows (PowerShell + robocopy)

```powershell
$dest = "C:\\path\\to\\your\\project\\skills"
mkdir $dest -Force
robocopy .\\skills $dest /E /XO
```

`/E` copies subdirectories; `/XO` skips older destination files.

## 3) Keep Skills Up to Date

Update your local clone, then re-run the sync step (if you are copying into another project):

```bash
git pull
rsync -a --exclude ".git" --exclude ".DS_Store" skills/ ./skills/
```

---

Skill directory reference:

```
https://github.com/Ariel-Rodriguez/programming-skills/tree/main/skills
```

## Global Skills Folder (Optional)

If your AI tool supports a global skills directory, you can sync there instead. Check the tool’s documentation (e.g., Gemini, Claude, Codex) for the exact path and configuration options.
