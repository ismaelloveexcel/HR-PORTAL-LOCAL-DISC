# “My Agent” — Deployment Guardrails

This agent keeps the custom “my agent” aligned with the repo’s Azure OIDC deployment pattern.

## Use when you need
- To run or review “my agent” deployments
- To prevent OIDC token failures
- To verify required secrets and workflow steps

## Rules
1. **OIDC permissions required**
   ```yaml
   permissions:
     id-token: write
     contents: read
   ```
2. **No client secret with `azure/login@v2`**  
   Only set `client-id`, `tenant-id`, and `subscription-id`.
3. **Mandatory GitHub secrets**  
   `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `DATABASE_URL`, `AUTH_SECRET_KEY`.
4. **Workflow to run**  
   Trigger “Deploy to Azure”, then verify `/api/health` and `/api/health/db`.

## References
- OIDC token failure context: `REVIEW_SUMMARY.md`
- Deployment workflow: `.github/workflows/deploy.yml`
