# Private weekly digest automation

The weekly digest runs locally on macOS so Supabase, SMTP, and recipient credentials never need to be uploaded to GitHub. GitHub Actions is intentionally not used for this job.

## Security model

- Store credentials only in the repository's ignored `.env` file.
- Never put credentials in GitHub Actions variables. Variables are not intended for secrets and can be visible to workflow users.
- Never commit `.env`, generated digests, or scheduler logs.
- Use a dedicated SMTP app password instead of the primary mailbox password.
- Keep `SUPABASE_SERVICE_ROLE_KEY` local. It bypasses Row Level Security and must be treated as a high-privilege credential.

## Required local configuration

Add these entries to `.env` without committing the file:

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-app-password
SMTP_STARTTLS=true
WEEKLY_DIGEST_FROM=sender@example.com
WEEKLY_DIGEST_TO=recipient@example.com
```

`SMTP_USERNAME` may be blank for a trusted local relay. `SMTP_PORT` defaults to `587`, and `SMTP_STARTTLS` defaults to `true`.

## Test delivery manually

From the repository root:

```bash
.venv/bin/python scripts/send_weekly_digest.py
```

The command refuses to send demo data when live Supabase access is unavailable. It also fails clearly when required SMTP or recipient settings are absent.

To archive the Markdown body locally as well as email it, add an ignored output path to `.env`:

```dotenv
WEEKLY_DIGEST_OUTPUT=.local/weekly-digest.md
```

## Schedule delivery with macOS launchd

The provided template runs every Monday at 9:00 AM in the Mac's local timezone.

1. Create local output storage:

   ```bash
   mkdir -p .local
   ```

2. Copy the template and replace the project-root placeholder:

   ```bash
   sed "s|__PROJECT_ROOT__|$PWD|g" \
     config/com.resume-analytics.weekly-digest.plist.example \
     > /tmp/com.resume-analytics.weekly-digest.plist
   plutil -lint /tmp/com.resume-analytics.weekly-digest.plist
   cp /tmp/com.resume-analytics.weekly-digest.plist \
     "$HOME/Library/LaunchAgents/com.resume-analytics.weekly-digest.plist"
   ```

3. Load and immediately test the job:

   ```bash
   launchctl bootstrap "gui/$(id -u)" \
     "$HOME/Library/LaunchAgents/com.resume-analytics.weekly-digest.plist"
   launchctl kickstart -k "gui/$(id -u)/com.resume-analytics.weekly-digest"
   ```

4. Inspect status and logs:

   ```bash
   launchctl print "gui/$(id -u)/com.resume-analytics.weekly-digest"
   tail -n 100 .local/weekly-digest.log
   tail -n 100 .local/weekly-digest-error.log
   ```

## Disable or update the schedule

Unload it before editing or removing the installed plist:

```bash
launchctl bootout "gui/$(id -u)/com.resume-analytics.weekly-digest"
```

After changing the template or installed plist, bootstrap it again using the command above.

## Operational notes

- The Mac must be powered on and the user logged in near the scheduled time. `launchd` normally runs a missed calendar job when the Mac wakes.
- The scheduler uses the repository's `.venv`; keep dependencies installed with `.venv/bin/pip install -r requirements.txt`.
- Moving the repository requires regenerating and reinstalling the plist because it contains absolute paths.
- The dashboard's Weekly Digest tab remains available without SMTP and supports manual Markdown downloads.
