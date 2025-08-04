# 🚀 Chicago Taxi Fare API - Production Deployment Guide

## 📋 Overview

This guide covers deploying the Chicago Taxi Fare Prediction API to production using multiple deployment strategies.

## 🏗️ Architecture

```
Internet → Load Balancer → API Instances → Model Files
                      ↓
                 Monitoring & Logging
```

## 🎯 Deployment Options

### 1. 🟣 **Heroku (Easiest - $7/month)**

**Best for:** Quick MVP, small scale, minimal DevOps

```bash
# Prerequisites
brew install heroku/brew/heroku  # macOS
# or: https://devcenter.heroku.com/articles/heroku-cli

# Deploy
chmod +x deploy_heroku.sh
./deploy_heroku.sh
```

**Pros:**
- ✅ Zero DevOps overhead
- ✅ Automatic HTTPS
- ✅ Easy scaling
- ✅ Built-in monitoring

**Cons:**
- ❌ More expensive at scale
- ❌ Limited customization
- ❌ Ephemeral filesystem

---

### 2. 🌊 **DigitalOcean (Recommended - $5/month)**

**Best for:** Startups, cost-effective scaling

```bash
# Prerequisites
brew install doctl  # macOS
doctl auth init

# Deploy
chmod +x deploy_digitalocean.sh
./deploy_digitalocean.sh
```

**Pros:**
- ✅ Cost-effective
- ✅ Simple deployment
- ✅ Auto-scaling
- ✅ Great performance

**Cons:**
- ❌ Fewer services than AWS
- ❌ Limited global regions

---

### 3. ☁️ **AWS (Enterprise - $20+/month)**

**Best for:** Enterprise scale, complex requirements

```bash
# Prerequisites
aws configure
aws cloudformation validate-template --template-body file://deploy_aws.yml

# Deploy
aws cloudformation create-stack \
  --stack-name chicago-taxi-api \
  --template-body file://deploy_aws.yml \
  --parameters ParameterKey=ContainerImage,ParameterValue=your-image-url \
  --capabilities CAPABILITY_NAMED_IAM
```

**Pros:**
- ✅ Unlimited scaling
- ✅ Enterprise features
- ✅ Global presence
- ✅ Advanced monitoring

**Cons:**
- ❌ Complex setup
- ❌ Higher costs
- ❌ Steep learning curve

---

### 4. 🐳 **Docker (Any Platform)**

**Best for:** Consistent deployment across environments

```bash
# Build image
docker build -t chicago-taxi-api .

# Run locally
docker-compose up

# Deploy to any Docker-compatible platform
docker run -p 8000:8000 \
  -e MODEL_PATH=/app/models \
  -e WEB_CONCURRENCY=4 \
  chicago-taxi-api
```

---

## 🔧 Production Checklist

### ✅ Pre-Deployment

- [ ] **Model files present** in `models/` directory
- [ ] **Requirements.txt** updated
- [ ] **Environment variables** configured
- [ ] **Secrets** properly managed
- [ ] **Health checks** working
- [ ] **Tests** passing

### ✅ Security

- [ ] **HTTPS** enabled
- [ ] **API rate limiting** configured
- [ ] **Input validation** implemented
- [ ] **Error handling** doesn't expose internals
- [ ] **Secrets** not in code
- [ ] **Dependencies** vulnerability-free

### ✅ Performance

- [ ] **Load testing** completed
- [ ] **Auto-scaling** configured
- [ ] **Caching** strategy in place
- [ ] **Database** optimized (if used)
- [ ] **CDN** configured (if needed)

### ✅ Monitoring

- [ ] **Health checks** configured
- [ ] **Logging** centralized
- [ ] **Metrics** collection
- [ ] **Alerting** set up
- [ ] **Error tracking** enabled

### ✅ Disaster Recovery

- [ ] **Backups** automated
- [ ] **Recovery procedures** documented
- [ ] **Failover** tested
- [ ] **Data replication** configured

---

## 🌐 Environment Variables

```bash
# Required
MODEL_PATH=/app/models          # Path to model files
PORT=8000                       # Server port
WEB_CONCURRENCY=4              # Number of workers

# Optional
LOG_LEVEL=info                 # Logging level
SECRET_KEY=your-secret-key     # Flask secret key
DATABASE_URL=postgresql://     # Database connection
REDIS_URL=redis://             # Cache connection
```

---

## 📊 API Usage Examples

### Health Check
```bash
curl https://your-api-url.com/health
```

### Single Prediction
```bash
curl -X POST https://your-api-url.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "trip_miles": 5.2,
    "trip_seconds": 1800,
    "pickup_community_area": 73,
    "dropoff_community_area": 53,
    "trip_start_timestamp": "2021-06-15T14:30:00"
  }'
```

### Batch Prediction
```bash
curl -X POST https://your-api-url.com/batch_predict \
  -H "Content-Type: application/json" \
  -d '{
    "trips": [
      {
        "trip_miles": 2.1,
        "trip_seconds": 900,
        "pickup_community_area": 23,
        "dropoff_community_area": 32,
        "trip_start_timestamp": "2021-06-15T09:00:00"
      }
    ]
  }'
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Model files not found**
   ```bash
   # Check model files exist
   ls -la models/
   
   # Verify permissions
   chmod 644 models/*
   ```

2. **Memory issues**
   ```bash
   # Increase memory allocation
   export WEB_CONCURRENCY=2  # Reduce workers
   ```

3. **Performance issues**
   ```bash
   # Enable caching
   pip install redis
   export REDIS_URL=redis://localhost:6379
   ```

4. **Health check failures**
   ```bash
   # Test locally
   curl http://localhost:8000/health
   
   # Check logs
   docker logs container-name
   ```

---

## 📈 Scaling Guidelines

### Traffic Levels

| **Requests/Day** | **Deployment** | **Cost/Month** | **Setup Time** |
|------------------|----------------|----------------|----------------|
| < 10K | Heroku Basic | $7 | 15 min |
| 10K - 100K | DigitalOcean | $15 | 30 min |
| 100K - 1M | AWS Fargate | $50 | 2 hours |
| > 1M | Kubernetes | $200+ | 1 day |

### Performance Tuning

1. **Optimize workers**: `WEB_CONCURRENCY = (2 * CPU_cores) + 1`
2. **Enable caching**: Redis for repeated predictions
3. **Use CDN**: For static assets
4. **Database**: For prediction history
5. **Load balancing**: Multiple instances

---

## 🔒 Security Best Practices

1. **API Keys**: Use authentication for production
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Sanitize all inputs
4. **HTTPS**: Always use SSL/TLS
5. **Monitoring**: Watch for anomalies
6. **Updates**: Keep dependencies updated

---

## 📞 Support

### Quick Commands

```bash
# View logs
heroku logs --tail -a your-app        # Heroku
doctl apps logs your-app-id           # DigitalOcean
kubectl logs deployment/your-app       # Kubernetes

# Scale up
heroku ps:scale web=5 -a your-app     # Heroku
doctl apps update your-app-id         # DigitalOcean
kubectl scale deployment your-app --replicas=5  # Kubernetes

# Restart
heroku restart -a your-app            # Heroku
doctl apps restart your-app-id        # DigitalOcean
kubectl rollout restart deployment/your-app     # Kubernetes
```

### Getting Help

1. **Check logs** first
2. **Review health checks**
3. **Test locally** with same data
4. **Check resource usage**
5. **Verify environment variables**

---

## 🎯 Next Steps

1. **Choose deployment platform** based on your needs
2. **Set up monitoring** and alerting
3. **Configure CI/CD** pipeline
4. **Plan scaling** strategy
5. **Document procedures** for your team

---

**🚀 Your Chicago Taxi Fare API is ready for production!**