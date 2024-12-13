# Cloudflare Account ID

1. Visit https://dash.cloudflare.com
2. Select an account if prompted.
3. Under `Account Home`, select a `Domain` if available.
4. Scroll to the bottom of the page and observe to the right. 
5. Find your `Account ID` there.
6. Use this for `CLOUDFLARE_ACCOUNT_ID` environment variable.

# Cloudflare API Token

1. From the top navigation menu, on the far right, click the last option and select `Account Home`.
2. From the left navigation menu, towards the bottom, expand `Manage Account` and click `Account API Tokens`.
3. Click `Create Token` button.
4. Find `Workers AI` row and click `Use template` button next to it.
5. Optionally, set TTL start and end dates.
6. Click `Continue to summary`.
7. Verify details and click `Create Token`.
8. Copy the token.
9. Use this for `CLOUDFLARE_API_TOKEN` environment variable.

# (Optional) Cloudflare Workers API LLM

1. Visit https://developers.cloudflare.com/workers-ai/models/.
2. Under `Model Types`, select `Text Generation`.
3. Click a model card that you are interested in.
4. On the model description page look for `@<repo>/<author>/<model name>` under model's name.
5. Use this name, including `@...` for `MODEL_NAME` environment variable.
