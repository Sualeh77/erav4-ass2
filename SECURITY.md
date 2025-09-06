# 🔐 Security Guide for API Key Management

## Understanding Environment Variables in Docker

### Current Architecture:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Host .env     │───▶│  docker-compose  │───▶│   Container     │
│ GEMINI_API_KEY  │    │  reads & passes  │    │ receives value  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### File Hierarchy:
1. **Dockerfile**: `ENV GEMINI_API_KEY=""` (default/fallback)
2. **docker-compose.yml**: `GEMINI_API_KEY=${GEMINI_API_KEY}` (reads from host)
3. **Host .env**: `GEMINI_API_KEY=actual_key` (actual value)

**Result**: Host .env value overrides Dockerfile default.

## 🚀 AWS EC2 Deployment Options

### Option 1: AWS Systems Manager Parameter Store (Recommended)

**Pros:**
- ✅ Most secure - encrypted at rest
- ✅ Centralized secret management
- ✅ Access logging and auditing
- ✅ Fine-grained IAM permissions
- ✅ Automatic rotation support

**Setup:**
```bash
# 1. Store secret in Parameter Store
aws ssm put-parameter \
    --name "/tools-dashboard/gemini-api-key" \
    --value "your_actual_api_key" \
    --type "SecureString"

# 2. Create IAM role for EC2 with SSM permissions
# 3. Use the provided aws-deploy.sh script
```

**IAM Policy Required:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:GetParameters"
            ],
            "Resource": "arn:aws:ssm:*:*:parameter/tools-dashboard/*"
        }
    ]
}
```

### Option 2: EC2 .env File (Simple)

**Pros:**
- ✅ Simple to implement
- ✅ No additional AWS services
- ✅ Works immediately

**Cons:**
- ⚠️ File-based storage
- ⚠️ Manual management

**Setup:**
```bash
# On EC2 instance
echo "GEMINI_API_KEY=your_key" > .env
chmod 600 .env  # Owner read/write only
chown ec2-user:ec2-user .env
```

### Option 3: AWS Secrets Manager (Enterprise)

**For production environments:**
```bash
# Store in Secrets Manager
aws secretsmanager create-secret \
    --name "tools-dashboard/api-keys" \
    --description "API keys for Tools Dashboard" \
    --secret-string '{"gemini_api_key":"your_actual_key"}'

# Retrieve in application
aws secretsmanager get-secret-value \
    --secret-id "tools-dashboard/api-keys"
```

## 🛡️ Security Best Practices

### 1. Never Commit Secrets
```bash
# ✅ Good - in .gitignore
.env
*.pem
secrets/

# ❌ Bad - committed to repo
GEMINI_API_KEY=abc123  # in code
```

### 2. File Permissions
```bash
# ✅ Secure permissions
chmod 600 .env          # Owner read/write only
chmod 400 *.pem         # Owner read only

# ❌ Insecure permissions
chmod 644 .env          # World readable
chmod 777 secrets/      # World writable
```

### 3. Environment Separation
```bash
# ✅ Different keys per environment
/dev/tools-dashboard/gemini-api-key
/staging/tools-dashboard/gemini-api-key  
/prod/tools-dashboard/gemini-api-key

# ❌ Same key everywhere
GEMINI_API_KEY=same_key_for_all_envs
```

### 4. Access Logging
```bash
# ✅ Monitor secret access
aws logs filter-log-events \
    --log-group-name /aws/ssm/parameter-store \
    --filter-pattern "tools-dashboard"
```

## 🚀 Quick Deployment Commands

### For Development:
```bash
# Local development
echo "GEMINI_API_KEY=your_key" > .env
docker-compose up
```

### For AWS EC2 (Simple):
```bash
# 1. Upload project (excluding .env)
rsync -av --exclude='.env' . ec2-user@your-ec2:/home/ec2-user/tools-dashboard/

# 2. Create .env on EC2
ssh ec2-user@your-ec2 "cd tools-dashboard && echo 'GEMINI_API_KEY=your_key' > .env && chmod 600 .env"

# 3. Start application
ssh ec2-user@your-ec2 "cd tools-dashboard && docker-compose up -d"
```

### For AWS EC2 (Parameter Store):
```bash
# Use the provided aws-deploy.sh script
./aws-deploy.sh
```

## 🔍 Security Checklist

- [ ] API keys not in source code
- [ ] .env files in .gitignore
- [ ] Secure file permissions (600 for secrets)
- [ ] Different keys per environment
- [ ] Regular key rotation
- [ ] Access monitoring enabled
- [ ] Principle of least privilege (IAM)
- [ ] Encrypted storage (Parameter Store/Secrets Manager)

## 🚨 What NOT to Do

❌ **Never do these:**
```bash
# Don't put secrets in Dockerfile
ENV GEMINI_API_KEY=actual_key_here

# Don't commit .env files
git add .env

# Don't use world-readable permissions
chmod 644 .env

# Don't hardcode in source code
api_key = "hardcoded_key_here"

# Don't share keys in chat/email
"Hey, the API key is abc123..."

# Don't use same key for all environments
prod_key = dev_key = staging_key
```

## 📞 Emergency Response

**If API key is compromised:**
1. **Immediately** revoke the key from Google AI Studio
2. Generate new API key
3. Update Parameter Store/secrets
4. Restart applications
5. Review access logs
6. Update any documentation

---

**Remember**: Security is not a one-time setup - it's an ongoing practice! 🛡️
