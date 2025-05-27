from fastapi import HTTPException

def get_fraud_score(payment):
    return 0.0

def get_risk_level(payment):
    return "low"

def check_permissions(user, required_role="admin"):
    if not (any(role.name == required_role for role in (user.roles or []))):
         raise HTTPException(status_code= 403, detail="Not authorized.")
    return (user) 