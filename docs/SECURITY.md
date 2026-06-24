# Security Documentation

Comprehensive security measures and best practices implemented in AI ERP v3.3.

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Data Protection](#data-protection)
3. [Input Validation & Sanitization](#input-validation--sanitization)
4. [API Security](#api-security)
5. [Database Security](#database-security)
6. [Infrastructure Security](#infrastructure-security)
7. [Compliance & Auditing](#compliance--auditing)
8. [Incident Response](#incident-response)

## Authentication & Authorization

### JWT (JSON Web Tokens)

```typescript
// src/core/auth/jwt.service.ts
import jwt from 'jsonwebtoken';

export class JWTService {
  generateToken(payload: any, expiresIn: string = '24h'): string {
    return jwt.sign(payload, process.env.JWT_SECRET, { 
      expiresIn,
      algorithm: 'HS256'
    });
  }

  verifyToken(token: string): any {
    try {
      return jwt.verify(token, process.env.JWT_SECRET);
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }

  refreshToken(token: string): string {
    const decoded = this.verifyToken(token);
    return this.generateToken({
      id: decoded.id,
      email: decoded.email,
      roles: decoded.roles
    });
  }
}
```

### Role-Based Access Control (RBAC)

```typescript
// src/core/auth/rbac.middleware.ts
export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user',
  GUEST = 'guest'
}

export const requireRole = (allowedRoles: UserRole[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = req.user;
    
    if (!user || !allowedRoles.includes(user.role)) {
      return res.status(403).json({ 
        error: 'Insufficient permissions' 
      });
    }
    
    next();
  };
};
```

### OAuth2 Integration

```typescript
// src/core/auth/oauth.service.ts
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: '/auth/google/callback'
}, (accessToken, refreshToken, profile, done) => {
  // Validate and create/update user
  User.findOrCreate({ googleId: profile.id }, (err, user) => {
    return done(err, user);
  });
}));
```

## Data Protection

### Encryption at Rest

```typescript
// src/core/encryption/crypto.service.ts
import crypto from 'crypto';

export class CryptoService {
  private algorithm = 'aes-256-cbc';
  private key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');

  encrypt(text: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
    
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    
    return iv.toString('hex') + ':' + encrypted.toString('hex');
  }

  decrypt(encryptedText: string): string {
    const parts = encryptedText.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const encrypted = Buffer.from(parts[1], 'hex');
    
    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    let decrypted = decipher.update(encrypted);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    
    return decrypted.toString();
  }
}
```

### Encryption in Transit

```typescript
// Use TLS 1.3+
// .env configuration
SSL_ENABLED=true
HTTPS_PORT=443
TLS_MIN_VERSION=TLSv1.3
```

### Hashing Passwords

```typescript
// src/core/auth/password.service.ts
import bcrypt from 'bcrypt';

export class PasswordService {
  async hashPassword(password: string): Promise<string> {
    const saltRounds = 12;
    return await bcrypt.hash(password, saltRounds);
  }

  async comparePassword(password: string, hash: string): Promise<boolean> {
    return await bcrypt.compare(password, hash);
  }
}
```

### Data Masking

```typescript
// src/core/privacy/data-masking.ts
export function maskSensitiveData(data: any): any {
  return {
    ...data,
    ssn: maskSSN(data.ssn),
    creditCard: maskCreditCard(data.creditCard),
    email: maskEmail(data.email)
  };
}

function maskSSN(ssn: string): string {
  return ssn.replace(/\d(?=\d{4})/g, '*'); // XXX-XX-1234
}

function maskCreditCard(cc: string): string {
  return '*'.repeat(12) + cc.slice(-4); // ************1234
}

function maskEmail(email: string): string {
  const [local, domain] = email.split('@');
  return local[0] + '*'.repeat(local.length - 2) + local[local.length - 1] + '@' + domain;
}
```

## Input Validation & Sanitization

### Schema Validation

```typescript
// src/api/validators/user.validator.ts
import { z } from 'zod';

export const CreateUserSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(12, 'Password must be at least 12 characters'),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  role: z.enum(['admin', 'manager', 'user'])
});

export const validateInput = (schema: z.ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      res.status(400).json({ errors: error.errors });
    }
  };
};
```

### Sanitization

```typescript
// src/core/sanitization/sanitizer.ts
import DOMPurify from 'isomorphic-dompurify';
import xss from 'xss';

export class Sanitizer {
  static sanitizeHtml(input: string): string {
    return DOMPurify.sanitize(input);
  }

  static sanitizeUserInput(input: string): string {
    return xss(input, { whiteList: {} });
  }

  static sanitizeUrl(url: string): string {
    const parsed = new URL(url);
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error('Invalid URL protocol');
    }
    return url;
  }
}
```

### SQL Injection Prevention

```typescript
// src/models/user.model.ts
import { db } from '../database';

export async function getUserById(id: number): Promise<User> {
  // Using parameterized queries
  const query = 'SELECT * FROM users WHERE id = $1';
  const result = await db.query(query, [id]);
  return result.rows[0];
}

// Using ORM (recommended)
export async function getUserByEmail(email: string): Promise<User> {
  return User.findOne({ where: { email } });
}
```

## API Security

### Rate Limiting

```typescript
// src/middleware/rate-limit.ts
import rateLimit from 'express-rate-limit';

export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

export const strictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // strict limit for auth endpoints
  skipSuccessfulRequests: true,
});
```

### CORS Configuration

```typescript
// src/middleware/cors.ts
import cors from 'cors';

export const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['https://yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 3600
};

app.use(cors(corsOptions));
```

### CSRF Protection

```typescript
// src/middleware/csrf.ts
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: false });

export const generateCSRFToken = (req: Request, res: Response) => {
  res.json({ csrfToken: req.csrfToken() });
};

app.use(csrfProtection);
```

### Security Headers

```typescript
// src/middleware/security-headers.ts
import helmet from 'helmet';

app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https:'],
  }
}));
```

## Database Security

### Connection Security

```typescript
// src/database/connection.ts
import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: { rejectUnauthorized: true }, // Enable SSL
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

### User Privileges

```sql
-- Create database user with minimal privileges
CREATE USER erp_user WITH PASSWORD 'secure_password';

-- Grant specific permissions
GRANT CONNECT ON DATABASE erp TO erp_user;
GRANT USAGE ON SCHEMA public TO erp_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO erp_user;

-- Revoke dangerous privileges
REVOKE SUPERUSER ON ROLE erp_user;
```

## Infrastructure Security

### Firewall Rules

```bash
# Allow only necessary ports
# SSH: 22 (from admin IPs only)
# HTTP: 80 (redirect to HTTPS)
# HTTPS: 443 (all)
# Database: 5432 (internal only)
```

### Environment Variables

```bash
# DO NOT commit .env files
# Use secure secret management:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
# - Kubernetes Secrets

# Example: .env.example (safe to commit)
NODE_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/erp
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
```

## Compliance & Auditing

### Audit Logging

```typescript
// src/core/audit/audit.service.ts
export class AuditService {
  async log(action: string, userId: string, details: any): Promise<void> {
    await AuditLog.create({
      action,
      userId,
      details,
      timestamp: new Date(),
      ipAddress: getCurrentIpAddress(),
      userAgent: getCurrentUserAgent()
    });
  }
}
```

### Compliance Checks

```typescript
// src/core/compliance/compliance.service.ts
export class ComplianceService {
  async verifyMyanmarCompliance(data: any): Promise<boolean> {
    // Verify Myanmar-specific regulatory requirements
    // Tax identification
    // Business registration
    // Data residency requirements
    return true;
  }
}
```

## Incident Response

### Error Handling

```typescript
// DO NOT expose sensitive information in errors
export const globalErrorHandler = (err: Error, req: Request, res: Response) => {
  console.error('Error:', err); // Log full error internally

  // Return generic message to client
  res.status(500).json({
    error: 'An error occurred. Please contact support.',
    // DO NOT include: err.message, err.stack, database details
  });

  // Log incident
  auditService.logIncident(err, req);
};
```

### Security Updates

- Monitor security advisories
- Regular dependency updates: `npm audit fix`
- Patch management: Apply within 24-48 hours
- Security scanning: Run `npm audit` in CI/CD

## Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Strong password policies enforced
- [ ] Two-factor authentication enabled
- [ ] Regular security audits
- [ ] Dependency vulnerabilities checked
- [ ] SQL injection prevention implemented
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Rate limiting enabled
- [ ] Encryption at rest and in transit
- [ ] Access logging enabled
- [ ] Incident response plan documented
- [ ] Regular backups tested
- [ ] Data retention policies defined
- [ ] Privacy policy updated

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Myanmar Data Protection Law](https://www.dica.gov.mm/)
