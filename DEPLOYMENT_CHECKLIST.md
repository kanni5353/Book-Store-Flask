# Production Deployment Checklist

## Pre-Deployment Steps

### 1. Environment Configuration
- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`: `python -c 'import secrets; print(secrets.token_hex(32))'`
- [ ] Configure database credentials (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) OR
- [ ] Configure `DATABASE_URL` for cloud platforms
- [ ] Create `.env` file with production values (NEVER commit this file!)

### 2. Code Verification
- [ ] Run tests: `python test_app.py`
- [ ] Verify no syntax errors: `python -m py_compile app.py`
- [ ] Check dependencies: `pip install -r requirements.txt`
- [ ] Test app locally: `FLASK_ENV=production python app.py`

### 3. Security Review
- [ ] No hardcoded credentials in code
- [ ] `.env` file is in `.gitignore`
- [ ] Strong SECRET_KEY configured
- [ ] Database credentials secured
- [ ] Run security scan if available

### 4. Database Preparation
- [ ] Database server accessible
- [ ] Database user has required permissions
- [ ] Backup existing data (if migrating)
- [ ] Test database connection

## Deployment Steps

### For Heroku
- [ ] Install Heroku CLI
- [ ] Login: `heroku login`
- [ ] Create app: `heroku create your-app-name`
- [ ] Add JawsDB: `heroku addons:create jawsdb:kitefin`
- [ ] Set environment variables:
  - [ ] `heroku config:set FLASK_ENV=production`
  - [ ] `heroku config:set SECRET_KEY=your-key`
- [ ] Deploy: `git push heroku main`
- [ ] Initialize database: `heroku run python init_db.py`
- [ ] Add sample data (optional): `heroku run python sample_data.py`
- [ ] Test: `heroku open`

### For Railway
- [ ] Install Railway CLI: `npm i -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Initialize: `railway init`
- [ ] Add MySQL database: `railway add`
- [ ] Set environment variables in dashboard
- [ ] Deploy: `railway up`
- [ ] Initialize database: `railway run python init_db.py`
- [ ] Test application

### For Render
- [ ] Create account at render.com
- [ ] Create MySQL database
- [ ] Copy Internal Database URL
- [ ] Create Web Service from GitHub
- [ ] Set environment variables:
  - [ ] FLASK_ENV=production
  - [ ] SECRET_KEY=your-key
  - [ ] DATABASE_URL=your-db-url
- [ ] Deploy
- [ ] Initialize database via Shell tab
- [ ] Test application

### For PythonAnywhere
- [ ] Create account at pythonanywhere.com
- [ ] Clone repository in Bash console
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Create MySQL database from Databases tab
- [ ] Configure `.env` file with credentials
- [ ] Initialize database: `python init_db.py`
- [ ] Configure WSGI file
- [ ] Set static files path
- [ ] Reload web app
- [ ] Test application

## Post-Deployment Verification

### 1. Basic Functionality
- [ ] Home page loads: `https://your-app.com/`
- [ ] Health check works: `https://your-app.com/health`
- [ ] Signup page loads and works
- [ ] Login page loads and works
- [ ] Dashboard accessible after login
- [ ] Can add new books
- [ ] Can sell books
- [ ] Can view stock
- [ ] Can view sales
- [ ] Logout works

### 2. Performance & Monitoring
- [ ] Response times acceptable
- [ ] Database queries performing well
- [ ] No errors in logs
- [ ] Health check endpoint responding
- [ ] Set up monitoring (UptimeRobot, etc.)

### 3. Security Verification
- [ ] HTTPS enabled
- [ ] No sensitive data in logs
- [ ] Session management working
- [ ] Password hashing working
- [ ] SQL injection protection working
- [ ] Check security headers

### 4. Error Handling
- [ ] Test with invalid inputs
- [ ] Test database connection failures
- [ ] Test session expiry
- [ ] Check error messages don't leak info
- [ ] Verify error logging works

## Ongoing Maintenance

### Daily
- [ ] Monitor health check endpoint
- [ ] Check for error logs
- [ ] Verify application uptime

### Weekly
- [ ] Review application logs
- [ ] Check database performance
- [ ] Monitor disk space usage
- [ ] Review user activity

### Monthly
- [ ] Update dependencies (security patches)
- [ ] Backup database
- [ ] Review and rotate secrets
- [ ] Check for security vulnerabilities
- [ ] Review and optimize performance

## Troubleshooting Quick Reference

### Database Connection Failed
1. Verify credentials in environment variables
2. Check database server is running
3. Test connection from deployment environment
4. Check firewall/security group settings

### Import Errors
1. Ensure all dependencies in requirements.txt
2. Verify Python version compatibility
3. Check virtual environment is activated
4. Reinstall dependencies

### Static Files Not Loading
1. Verify static files path configured
2. Check file permissions
3. Clear browser cache
4. Check platform-specific static file settings

### Application Won't Start
1. Check application logs
2. Verify all environment variables set
3. Test locally first
4. Check port configuration
5. Verify WSGI configuration

## Support Resources

- **Documentation**: README.md
- **Issues**: GitHub Issues page
- **Heroku Docs**: https://devcenter.heroku.com
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **PythonAnywhere**: https://help.pythonanywhere.com

## Emergency Procedures

### Application Down
1. Check health endpoint
2. Review recent deployments
3. Check logs for errors
4. Verify database connection
5. Rollback if necessary

### Database Issues
1. Check database service status
2. Verify credentials haven't changed
3. Check connection limits
4. Restore from backup if needed

### Security Incident
1. Rotate all secrets immediately
2. Review logs for suspicious activity
3. Check for unauthorized access
4. Update security patches
5. Notify users if data compromised

---

**Last Updated**: 2026-01-07
**Version**: 1.0.0
