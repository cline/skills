---
name: dr-bedrock
description: Troubleshoot local AWS Bedrock authentication and region configuration for the Cline CLI as Dr. Bedrock. Use when users report Bedrock CLI errors, AWS profile/default-chain issues, credential_process/SSO/IAM credential failures, missing region, AccessDenied, model access, or provider config problems.
---

# Dr. Bedrock: Cline CLI Bedrock Auth Troubleshooter

Use this skill to diagnose local AWS Bedrock auth/configuration for the Cline CLI and report likely causes plus user-actionable fixes. This skill identifies problems only.

## Invocation rule

When this skill is invoked, the first thing you say to the user must always be exactly:

```text
Paging Dr. Bedrock...
```

Then proceed with diagnostics or reporting.

## Hard safety rules

- **DO NOT make any file changes on the system.** You are not fixing the problem, only identifying it.
- **DO NOT read or print sensitive credentials.** If reading a file that may contain credentials, use a command that filters or redacts credential values before they reach the transcript.
- **DO NOT suggest code changes in Cline.** Suggest user fixes: AWS auth setup, Cline CLI upgrade, reconfigure provider, export environment variables, refresh SSO, request Bedrock model access, etc.
- Avoid cost-incurring model invocations unless the user explicitly asks for a live invocation test. Prefer STS identity and Bedrock model-list/access checks.

## What to determine

Classify the likely auth scheme, then validate region, credentials, Cline config, and Bedrock model access.

Auth schemes to consider:

1. **Bedrock API key**: Cline config has `apiKey` or `aws.authentication: "api-key"`.
2. **Direct IAM keys in Cline config**: `aws.accessKey` + `aws.secretKey`, optional `aws.sessionToken`.
3. **Named AWS profile**: `aws.authentication: "profile"` and `aws.profile`, or `AWS_PROFILE`.
4. **Default AWS provider chain**: `aws.authentication: "iam"` or profile auth with no saved profile name.
5. **AWS IAM Identity Center / SSO**: profile contains `sso_session`, `sso_start_url`, `sso_account_id`, or `sso_role_name`.
6. **credential_process**: profile contains `credential_process`.
7. **Assume role profile**: profile contains `role_arn` with `source_profile`, `credential_source`, or web identity.
8. **Web identity / OIDC**: `AWS_ROLE_ARN` + `AWS_WEB_IDENTITY_TOKEN_FILE` or profile web identity settings.
9. **ECS/EC2 metadata**: container metadata env vars or IMDS on EC2.

## Known Cline CLI Bedrock failure modes

Use these as recognition patterns, not as code-change recommendations:

| Symptom | Likely cause | User-facing fix |
|---|---|---|
| `AWS region setting is missing. Pass it using the 'region' parameter or the AWS_REGION environment variable.` | Older CLI provider path did not forward Bedrock region/options to the gateway (#10770; fixed by PR #10807 / related #10818). | Upgrade Cline CLI. Work around by exporting `AWS_REGION=<region>` and reconfiguring Bedrock if upgrade is not possible. |
| Profile auth says provider configured, then no provider is ready | Older readiness logic treated Bedrock like API-key-only (#6958). | Upgrade Cline CLI and re-run Bedrock provider setup. |
| `AWS credential provider failed: Could not load credentials from any providers` with `credential_process` | Missing/unsaved profile name, shared config not loaded, bad `credential_process`, or affected CLI build (#10930; PR #10932; legacy migration PR #10943). | Upgrade Cline CLI; ensure `aws.profile` or `AWS_PROFILE` names the profile; try `AWS_SDK_LOAD_CONFIG=1`; verify `aws sts get-caller-identity --profile <profile>`. |
| Migrated config has `aws.authentication: "profile"` but no `aws.profile` | Legacy migration dropped `awsProfile` when old `awsUseProfile` was absent (#10943). | Upgrade Cline CLI and re-run migration, or reconfigure Bedrock so the profile name is saved. |
| API-key Bedrock auth not recognized or mixed up with region env | Older auth mapping before API-key alignment (#10731). | Upgrade Cline CLI; confirm Cline config uses Bedrock API key auth and still has a region. |
| ACP/editor integration asks for Cline/ChatGPT auth even though CLI Bedrock works | Older ACP auth readiness issue (#9404). | Upgrade Cline CLI and verify ACP uses the same config directory. |
| Custom application inference profile ARN cannot be entered/used | Older CLI model picker limitation (#9244/#9271). | Upgrade Cline CLI; use custom/ARN model entry flow if available. |

## Safe diagnostics workflow

### 1. Establish versions and config location

Run safe read-only commands:

```sh
cline --version 2>/dev/null || npx cline --version 2>/dev/null || true
node --version 2>/dev/null || true
aws --version 2>/dev/null || true
pwd
```

Ask whether the user runs Cline with `--config <dir>`. If yes, inspect that config directory; otherwise inspect `~/.cline/data`.

### 2. Inspect Cline provider config with redaction

Never print raw provider/secrets files. Prefer `jq`; otherwise use Node.

```sh
CLINE_DATA_DIR="${CLINE_DATA_DIR:-$HOME/.cline/data}"
PROVIDERS="$CLINE_DATA_DIR/settings/providers.json"

if [ -f "$PROVIDERS" ] && command -v jq >/dev/null 2>&1; then
  jq '
    def redact:
      if type == "object" then
        with_entries(if (.key|test("(?i)(key|secret|token|password|credential)")) then .value="<redacted>" else .value=(.value|redact) end)
      elif type == "array" then map(redact)
      else . end;
    .providers.bedrock.settings? | redact
  ' "$PROVIDERS"
elif [ -f "$PROVIDERS" ]; then
  node -e '
    const fs=require("fs"); const p=process.argv[1];
    const v=JSON.parse(fs.readFileSync(p,"utf8"));
    const r=(x)=>Array.isArray(x)?x.map(r):x&&typeof x==="object"?Object.fromEntries(Object.entries(x).map(([k,v])=>[k,/(key|secret|token|password|credential)/i.test(k)?"<redacted>":r(v)])):x;
    console.log(JSON.stringify(r(v.providers?.bedrock?.settings), null, 2));
  ' "$PROVIDERS"
else
  echo "No providers.json at $PROVIDERS"
fi
```

Interpretation:

- `provider` should be `bedrock`.
- `model` should be present.
- `aws.region` or top-level `region` should be present unless `AWS_REGION`/`AWS_DEFAULT_REGION` supplies it.
- If `aws.authentication` is `profile` but there is no `aws.profile` and no `AWS_PROFILE`, Cline will probably use the default AWS SDK credential chain. **This is not a failure mode by itself.** Treat it as healthy if the default-chain AWS identity and Bedrock checks succeed.
- If `aws.authentication` is `iam`, Cline is likely using the default AWS SDK chain.
- If `apiKey` is present or `aws.authentication` is `api-key`, this is Bedrock API key auth; AWS IAM profile checks may not apply, but region still does.

Also inspect legacy files only with redaction/key-presence checks if migration is suspected:

```sh
LEGACY="$CLINE_DATA_DIR/globalState.json"
SECRETS="$CLINE_DATA_DIR/secrets.json"
[ -f "$LEGACY" ] && jq '{awsRegion, awsAuthentication, awsUseProfile, awsProfile, awsUseCrossRegionInference, awsUseGlobalInference, awsBedrockUsePromptCache}' "$LEGACY" 2>/dev/null || true
[ -f "$SECRETS" ] && jq 'keys | map(select(test("(?i)(aws|bedrock)")))' "$SECRETS" 2>/dev/null || true
```

Do not print values from `secrets.json`.

### 3. Inspect AWS environment safely

Environment credentials can override profile/default-chain behavior. Print presence, not credential values:

```sh
python3 - <<'PY'
import os, re
safe = ["AWS_PROFILE","AWS_REGION","AWS_DEFAULT_REGION","AWS_CONFIG_FILE","AWS_SHARED_CREDENTIALS_FILE","AWS_SDK_LOAD_CONFIG"]
secretish = ["AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_SESSION_TOKEN","AWS_SECURITY_TOKEN"]
for k in safe:
    if k in os.environ:
        print(f"{k}={os.environ[k]}")
for k in secretish:
    if k in os.environ:
        print(f"{k}=<set redacted>")
for k in ["AWS_ROLE_ARN","AWS_WEB_IDENTITY_TOKEN_FILE","AWS_CONTAINER_CREDENTIALS_RELATIVE_URI","AWS_CONTAINER_CREDENTIALS_FULL_URI"]:
    if k in os.environ:
        v = os.environ[k]
        if k == "AWS_ROLE_ARN": v = re.sub(r"arn:aws[a-z-]*:iam::\d{12}:", "arn:aws:iam::<account>:", v)
        print(f"{k}={v}")
PY
```

Flag these issues:

- `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` are set unexpectedly: they can take precedence over profiles and point Cline at the wrong account.
- `AWS_PROFILE` differs from Cline `aws.profile`: Cline should use the saved profile when present; otherwise environment/default chain may be used. Only treat this as a likely issue if the resolved identity/account/region is demonstrably wrong for the intended Bedrock access.
- No region in Cline config or env: Bedrock calls will fail.
- Temporary env keys are set without `AWS_SESSION_TOKEN`: STS-derived credentials will fail.

### 4. Inspect AWS config/credentials files without secrets

List profile sections and non-secret key names. Do not print access key values.

```sh
AWS_CONFIG_FILE="${AWS_CONFIG_FILE:-$HOME/.aws/config}"
AWS_SHARED_CREDENTIALS_FILE="${AWS_SHARED_CREDENTIALS_FILE:-$HOME/.aws/credentials}"

for f in "$AWS_CONFIG_FILE" "$AWS_SHARED_CREDENTIALS_FILE"; do
  echo "--- $f ---"
  [ -f "$f" ] || { echo "missing"; continue; }
  awk '
    /^\[/ { section=$0; print section; next }
    /^[[:space:]]*(aws_access_key_id|aws_secret_access_key|aws_session_token)[[:space:]]*=/ { print "  " $1 "=<redacted>"; next }
    /^[[:space:]]*(region|sso_session|sso_start_url|sso_region|sso_account_id|sso_role_name|role_arn|source_profile|credential_source|web_identity_token_file|credential_process)[[:space:]]*=/ {
      key=$1; sub(/[[:space:]]*=.*/, "", key)
      if (key ~ /role_arn/) print "  " key "=<present redacted>";
      else if (key ~ /credential_process/) print "  " key "=<present redacted>";
      else print "  " $0
    }
  ' "$f"
done
```

Interpretation:

- In `~/.aws/config`, named profiles are `[profile name]`; in `~/.aws/credentials`, they are `[name]`.
- A profile with `credential_process` should work through the AWS SDK chain in fixed CLI builds, but it must be the active profile.
- SSO profiles require a valid cached login: run `aws sso login --profile <profile>` as the user if expired.
- Assume-role profiles require the source profile or credential source to be valid.

### 5. Validate AWS identity without exposing credentials

Use the likely profile and region. If no profile is configured, omit `--profile` to test the default chain.

```sh
PROFILE_ARG="--profile <profile>"   # replace or leave empty for default chain
REGION_ARG="--region <region>"      # replace with Cline/AWS region

aws sts get-caller-identity $PROFILE_ARG --output json
aws configure list $PROFILE_ARG
```

`get-caller-identity` does not reveal secret credentials, but account IDs/role names can be sensitive. Redact them in the final report unless the user already shared them.

Evaluation rules:

- If Cline is using the default credential chain and `aws sts get-caller-identity` succeeds without `--profile`, that auth path looks good unless there is direct evidence that Cline runs in a different environment.
- If `aws configure list` reports credential source/type as `login` and STS plus Bedrock list/get model calls succeed, treat the AWS CLI login/default-chain path as working. Do **not** claim Cline cannot use it unless there is an actual Cline error or version-specific evidence.
- A missing saved `aws.profile` is only a problem when the user intended a specific non-default profile and the default-chain identity is wrong or cannot access Bedrock.
- Absence of `~/.aws/credentials`, SSO fields, `credential_process`, or `AWS_PROFILE` is not a problem when another default-chain source resolves successfully.

Fix guidance by failure:

- SSO token expired: `aws sso login --profile <profile>`.
- Process provider failed: confirm the profile selected by Cline is the one with `credential_process`; test `aws sts get-caller-identity --profile <profile>`; ensure the process is executable and returns AWS process-credential JSON.
- Cannot find profile: set/reconfigure Cline `aws.profile`, export `AWS_PROFILE`, or fix section names in AWS files.
- Env keys point to wrong account: unset them or launch Cline from a shell with the intended env.

### 6. Validate Bedrock region/model access without invoking a model

```sh
aws bedrock list-foundation-models $PROFILE_ARG $REGION_ARG --by-output-modality TEXT --output table
```

If the selected model is known, also check availability where supported:

```sh
aws bedrock get-foundation-model $PROFILE_ARG $REGION_ARG --model-identifier '<model-id>' --output json
```

Troubleshoot results:

- `AccessDeniedException`: identity lacks `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, list/get model permissions, Marketplace/model access permissions, or an SCP/permission boundary denies access.
- Model absent in region: choose a model/inference profile available in that region, change region, or use a valid cross-region/global inference profile.
- Anthropic first-time access: complete Bedrock model access / use-case form in the AWS account/organization. Marketplace permissions may be required for first-time enablement.
- GovCloud: third-party model access may need enablement in both linked commercial and GovCloud accounts; model availability differs by GovCloud region.
- Custom/application inference profile ARN: confirm the ARN region/account match the configured region/profile account and the identity can use that inference profile.

### 7. Rule out Bedrock errors that are not auth problems

If STS identity and Bedrock model listing work, do not force an auth diagnosis. Some Bedrock failures are request/history/model issues:

- `Invalid type for parameter ... image.source.bytes` or screenshot/history replay failures: likely Bedrock image bytes serialization, not auth (#10926 / PR #10928). Suggest upgrading Cline CLI and retrying a fresh task without replayed screenshot history.
- Context-window or token-limit errors that arrive as plain text: likely context overflow, not auth (#10838). Suggest compacting/starting a fresh task or upgrading Cline CLI for improved detection.
- `ValidationException` for a model ID/ARN: often wrong region, unsupported model ID, missing inference profile, or using an application inference profile ARN with the wrong account/region.
- Errors only after several successful turns usually indicate request content, history, model availability, quota, or context issues rather than credential resolution.

## Final report format

Use one of two output modes.

### Normal mode (default)

By default, keep the final answer concise and report only:

1. **Recommended user fixes or next checks**: commands or UI actions. Do not suggest Cline code changes. If everything looks good, recommend no changes or only optional next checks.
2. **Diagnosis**: one of exactly these two outcomes:
   - **Likely issue found**: concise bullets with evidence and severity. Use this only for issues likely to break Cline, such as missing region, failed STS/default-chain resolution, wrong account/identity, expired SSO, failed `credential_process`, denied Bedrock access, unavailable selected model/region, or a known affected Cline version paired with the matching symptom.
   - **Looks good**: explicitly say the checked configuration/auth path looks good and no likely cause was found. Optionally include a short **Low-probability observations** addition for minor or theoretical findings that are unlikely to be causing the user's current issue.

The **Diagnosis** must be the last section in the report. In the diagnosis text, tell the user to scroll up for remediation steps or optional next checks.

At the end of normal-mode output, tell the user they can ask for deeper debugging information by saying something like: `Show me Dr. Bedrock's deep debugging details` or `Run Dr. Bedrock in verbose mode`.

### Verbose / deep debugging mode

If the user asks for more information, verbose output, deep debugging details, or asks to see how Dr. Bedrock reached the conclusion, include sections 1–4 before the normal-mode sections:

1. **Likely auth scheme**: API key, direct IAM keys, named profile, default chain, SSO, credential_process, assume role, web identity, ECS/EC2.
2. **Cline CLI config status**: provider/model/region present, auth fields present, profile saved or missing, likely affected by known CLI version issues.
3. **AWS local auth status**: env precedence, profile/default-chain health, STS identity test result (redacted).
4. **Bedrock access status**: region, model availability, permissions/model-access concerns.
5. **Recommended user fixes or next checks**: same as normal mode.
6. **Diagnosis**: same as normal mode and still the final section.

Do **not** invent an issue just to have one. If the config is coherent, AWS identity resolves, region is set, and Bedrock model/list checks pass, conclude **Looks good**. If something is merely different from a named-profile setup but still resolves through the default credential chain, do not call it a problem. If you noticed possible concerns that are weakly related or unlikely, include them only as optional **Low-probability observations** within the **Looks good** diagnosis rather than presenting them as root causes.

## Common fix snippets

- Upgrade Cline CLI:
  ```sh
  npm install -g cline@latest
  cline --version
  ```
- Launch with explicit profile/region:
  ```sh
  AWS_PROFILE=<profile> AWS_REGION=<region> AWS_SDK_LOAD_CONFIG=1 cline
  ```
- Refresh SSO:
  ```sh
  aws sso login --profile <profile>
  aws sts get-caller-identity --profile <profile>
  ```
- Reconfigure Bedrock in Cline CLI if saved profile/region is missing:
  ```sh
  cline auth
  ```
  Choose AWS Bedrock, leave API key blank for profile/default-chain auth, enter region, and enter the AWS profile name when prompted.
