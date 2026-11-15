# Gemini API setup for ANAS Studio

This is an optional server-side bridge. The Android APK never contains the Google Gemini key.

## 1. Deploy the Cloudflare Worker

1. Install Wrangler and authenticate: `npm install -g wrangler`, then `wrangler login`.
2. From this directory, set two secrets:
   ```sh
   wrangler secret put GEMINI_API_KEY
   wrangler secret put APP_ACCESS_TOKEN
   ```
3. Use a long random value for `APP_ACCESS_TOKEN` (at least 32 random characters). Keep it private.
4. Deploy: `wrangler deploy`.
5. Copy the resulting `https://...workers.dev` URL.

## 2. Configure the app

Open Gemini AI inside ANAS Studio, expand connection settings, and enter:
- Worker URL
- The same APP_ACCESS_TOKEN value

The Google key is entered only as the Worker secret. Never paste it into the app, GitHub source, or APK.

## 3. Verify

Try each task: script, rewrite, scenes, ideas. A 401 means the app token differs; a 503 means Worker secrets are missing; a 429 means quota/rate limiting.

## Security notes

- Restrict `ALLOWED_ORIGIN` to the published app origin.
- The shared app token is a basic gate, not per-user authentication or a full abuse-prevention system. Rotate it if exposed.
- Set usage quotas and billing alerts in Google AI Studio / Google Cloud.
- The Gemini API key must be restricted to Gemini API where supported.
