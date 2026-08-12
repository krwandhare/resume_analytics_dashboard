# Private weekly digest automation

The weekly digest runs locally on macOS using Gmail's API so Supabase and OAuth credentials never need to be uploaded to GitHub. GitHub Actions is intentionally not used for this job. Messages are sent from the authorized Gmail account to the address configured locally.

## Security model

- Store Supabase settings only in the repository's ignored `.env` file.
- Store the downloaded Google OAuth client and generated token only under ignored `.local/`.
- Never put credentials in GitHub Actions variables. Variables are not intended for secrets and can be visible to workflow users.
- Never commit `.env`, generated digests, or scheduler logs.
- The OAuth flow requests only `https://www.googleapis.com/auth/gmail.send`.
- No Google password, app password, OAuth client, or refresh token is committed or uploaded.
- Keep `SUPABASE_SERVICE_ROLE_KEY` local. It bypasses Row Level Security and must be treated as a high-privilege credential.

## Required local configuration

Add these entries to `.env` without committing the file. Set `WEEKLY_DIGEST_SENDER` to the authorized Gmail account or one of its configured send-as aliases:

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
WEEKLY_DIGEST_SENDER=sender@example.com
WEEKLY_DIGEST_RECIPIENT=recipient@example.com
```

Then configure Gmail OAuth once:

1. Create or select a Google Cloud project and enable the Gmail API.
2. Configure the OAuth consent screen. Use **External** while initially testing, then publish it to **Production** before relying on unattended weekly delivery. Google generally expires refresh tokens for external apps left in Testing after seven days.
3. While the app is in Testing, add the Gmail account you will authorize as a test user.
4. Create an OAuth client with application type **Desktop app**.
5. Create `.local/` and download the client JSON to `.local/google-oauth-client.json`.
6. Install dependencies and run the authorization command:

   ```bash
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python scripts/authorize_gmail.py
   ```

7. Approve the Gmail send-only permission in the browser. The command writes the refresh token to `.local/gmail-token.json`.

If consent is revoked or expires, run the authorization command again. Publishing the consent screen does not require Google verification when the app is for personal use by a small number of known accounts, although Google may display the unverified-app warning during consent.

## Test delivery manually

From the repository root:

```bash
.venv/bin/python scripts/send_weekly_digest.py
```

The command refuses to send demo data when live Supabase access is unavailable. It also fails clearly when OAuth client credentials or the local token are missing, consent is revoked, token refresh fails, or Gmail rejects the API request.

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
- The dashboard's Weekly Digest tab remains available without Gmail authorization and supports manual Markdown downloads.
