---
Class: Scene
Act: 4
cssclasses:
  - cornell-left
  - wide-page
  - cornell-border
dg-publish: true
operonId: kthmbrl
operonProjectStage: Default.Complete
priority: Zero
datetimeCreated: 2026-07-31T09:59:19
timestamp: 2026-07-31T10:34:49
Status: Complete
resource:
  - https://creativeprojects.github.io/resticprofile/
  - https://bford.info/cachedir/
  - https://restic.readthedocs.io/en/stable/040_backup.html#excluding-files
dateCompleted: 2026-07-31
---
>[!summary] A complete, automated, and hyper-efficient backup strategy using Restic and resticprofile.
> `restic backup . --tag "pre-huge-project" --exclude-caches` & `restic snapshots` to view

# Failsafe backup setup - Restic
If your current backup strategy involves dragging and dropping folders to an external drive, relying solely on standard cloud sync (which syncs deletions and corruptions instantly) or using basic zip scripts, you're missing out on the magic of modern backups.

**Why Restic is best the best at backing up your backups:**
1. **Deduplication:** Restic breaks your files into chunks and only saves the unique ones. If you rename a 1GB file, move it, or copy it, Restic backs it up instantly without using an extra byte of storage.
2. **True Snapshots:** Every time you back up, it creates a point-in-time snapshot. It looks like a full backup, but takes seconds to create and uses almost no extra space.
3. **Encrypted by Default:** Your data is encrypted before it ever leaves your computer. No one (not even your cloud provider) can read it without your password.
4. **Fast:** It is blazingly fast because it relies on metadata to detect changes and skips reading unmodified files entirely.
---
# Our Implementation Guide
Here is exactly how this repository (`archAive`) is set up, so you can replicate it for your own workflow.

### 1. Store Credentials Securely
Create a `.env` file in the root of the directory to hold the repository location and password. This prevents hardcoding passwords in scripts.

```bash
export RESTIC_REPOSITORY=/path/to/your/backup/destination
export RESTIC_PASSWORD='your_super_secret_password'
```

### 2. Smart Exclusions (`CACHEDIR.TAG`)
Backing up cache folders (like `node_modules` or `.tmp`) wastes massive amounts of space. Restic respects the "Cache Directory Tagging Standard".

To exclude a folder, simply create a file named `CACHEDIR.TAG` inside it, with this exact signature:
```text
Signature: 8a477f597d28d172789f06886806bc55
```
Restic will now completely ignore the contents of any folder containing this tag when you use the `--exclude-caches` flag.

>[!question] Where do you get the signature from?
> It comes directly from the [Cache Directory Tagging Standard](https://bford.info/cachedir/) created by Bryan Ford. It's an industry standard used by backup tools (like Restic, `tar`, etc.). Backup tools look for that *exact* hash to confirm that the file is genuinely an intentional cache tag and not just a random file you happened to name `CACHEDIR.TAG`

### 3. Automating with `resticprofile`
Writing bash scripts with `cron` can get messy. We use a tool called **[resticprofile](https://creativeprojects.github.io/resticprofile/)** to orchestrate everything natively.

First, make sure you have it installed:
```bash
brew install resticprofile
```

Create a file named `profiles.yaml` in your root folder:
```yaml
version: "1"

global:
  restic-lock-retry-after: 1m
  restic-stale-lock-age: 2h

default:
  # Automatically load the .env file
  env-file: "/Users/healmiy/archAive/.env"

  backup:
    source:
      - "/Users/healmiy/archAive"
    skip-if-unchanged: true
    exclude-caches: true
    tag:
      - "daily"
      - "archAive"

  retention:
    # Run the forget & prune policy automatically after each backup
    before-backup: false
    after-backup: true
    keep-daily: 7
    keep-weekly: 4
    keep-monthly: 6
    keep-yearly: 2
    prune: true
    
  # Schedule it to run daily at 2:00 PM (14:00)
  schedule: "14:00"
  schedule-permission: "user"
```

>[!tip] How does the retention policy actually work and how do I fine-tune it?
> Restic uses a smart, cascading strategy. Instead of keeping a set number of backups, it keeps the latest snapshot for each of the last 7 days, 4 weeks, 6 months, and 2 years. When a backup exceeds these rules, the `prune: true` command ensures Restic permanently deletes the orphaned data from the server to free up space. You can easily fine-tune this by adding rules like `keep-last: 5` (which always keeps your newest 5 backups)!

>[!question] Do I type `profiles.yaml backup` in the terminal? (why not restic specific name.yaml?)
>  `profiles.yaml` is the exact default filename that `resticprofile` looks for automatically. As long as you are inside the folder, you just type `resticprofile backup` and it silently finds and reads the file.
> You absolutely can rename it, but `resticprofile` won't find it automatically anymore. You just have to explicitly point to it using the `-c` flag. For example: `resticprofile -c resticBackingUp.yaml backup` or `resticprofile -c resticBackingUp.yaml schedule`.

---

# Cheat Sheet: Commands You Will Definitely Forget
Because `resticprofile` handles the heavy lifting, your daily interaction is minimal. But here are the vital commands for maintenance and manual overrides:

**Running Backups:**
* `resticprofile backup` — Manually trigger the backup using the `profiles.yaml` configuration.
* `resticprofile -c myCustomProfile.yaml backup` — How to run it if you renamed your YAML file.

>[!question] If I'm about to undertake a huge project, what command can I input manually to make a save point?
> If you're about to do something massive or destructive, it's highly recommended to make a "Named Save Point." Instead of just running the standard profile, use raw `restic` to inject a custom tag on the fly so you can easily spot it if you need to restore:
> ```bash
> source .env
> restic backup . --tag "pre-huge-project" --exclude-caches
> ```
> Later, running `restic snapshots` will show this specific backup tagged clearly as `"pre-huge-project"`

**Automation (macOS / Linux):**
* `resticprofile schedule` — Reads your YAML file and automatically registers a background service (`launchd` on macOS) to run your backups on schedule. No cron needed!
* `resticprofile status` — Check the status of your scheduled background tasks.

**Maintenance (Native Restic Commands):**
Even with automation, you should occasionally run maintenance checks.
* `source .env && restic check` — Verifies the structural integrity of your backup repository. Run this once a month to ensure your backups aren't corrupted.
* `source .env && restic snapshots` — View a clean list of all your historical point-in-time snapshots.

