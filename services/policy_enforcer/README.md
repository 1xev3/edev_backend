# Policy enforcement service

# Settings

### Setting up (If you not using Docker)
Set up your PosgreSQL

Create `.env` file in current folder with your data:
```ini
JWT_SECRET=YOUR_SECRET
POLICIES_CONFIG_PATH=policies.yaml
```

### Settings loading order:
1. .env file
2. Environment
3. Default fields

# Running
## Standalone:
```bash
source run.sh
```
or
```bash
uvicorn app.app:app --port 5100 --reload
```

## If you are using docker:

### Building from Dockerfile
Build service by using:
```bash
docker build -t "policy-enforcement-service:1.0" .
```

Configure your docker-compose file in `deploy` folder and run command:
```bash
docker-compose up -d
```

# Methods
All methods derived from services in policies.yaml

# Policies.yaml
```yaml
model: |
    [request_definition]
    r = sub, obj, act
    
    [policy_definition]
    p = sub_rule, obj, act
    
    [policy_effect]
    e = some(where (p.eft == allow))
    
    [matchers]
    m = eval(p.sub_rule) && keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)
services:
    - name: product-service
      entrypoint: http://localhost:5010/
      inject_token_in_swagger: True
    - name: ticket-service
      entrypoint: http://localhost:5001/
      inject_token_in_swagger: True
    - name: user-service
      entrypoint: http://localhost:5020/
      inject_token_in_swagger: True
policies:
    #PRODUCT SERVICE
    - service: product-service
      rule: r.sub.group_id == 1 #only admin
      resource: /products*
      methods: (POST)|(PUT)|(DELETE)
    - service: product-service
      resource: /products*
      methods: GET
      white_list: true

    #TICKET SERVICE
    - service: ticket-service
      rule: r.sub.group_id > 0
      resource: /tickets
      methods: GET
    - service: ticket-service
      rule: r.sub.group_id == 1
      resource: /tickets
      methods: POST
    - service: ticket-service
      rule: r.sub.group_id == 1
      resource: /tickets/*
      methods: (GET)|(POST)|(PUT)|(DELETE)

    #USER SERVICE
    - service: user-service
      rule: r.sub.group_id == 1 #only admin
      resource: /groups*
      methods: (GET)|(POST)|(PUT)|(DELETE)
    - service: user-service
      resource: /auth/*
      methods: POST
      white_list: true
    - service: user-service
      resource: /users/*
      methods: (GET)|(POST)|(PUT)|(DELETE)
      rule: r.sub.group_id > 0

    #REVIEW SERVICE
    - service: review-service
      rule: r.sub.group_id > 0
      resource: /reviews*
      methods: (GET)|(POST)|(PUT)|(DELETE)
```