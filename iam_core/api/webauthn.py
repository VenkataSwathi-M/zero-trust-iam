import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.auth.deps import get_current_identity
from iam_core.session.session_store import get_session, set_step_up, bump_trust

from iam_core.db.models import WebAuthnCredential

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    UserVerificationRequirement,
)

router = APIRouter(prefix="/agent/auth/webauthn", tags=["WebAuthn"])

RP_ID = os.getenv("WEBAUTHN_RP_ID", "192.168.31.211")  # must match domain you open frontend with
RP_NAME = os.getenv("WEBAUTHN_RP_NAME", "ZeroTrustIAM")

def _must_session(identity):
    sid = identity.get("sid")
    s = get_session(sid)
    if not s:
        raise HTTPException(401, "Session missing")
    return sid, s

# ---------- REGISTER (one time) ----------

@router.post("/register/options")
def register_options(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    sid, session = _must_session(identity)

    opts = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=agent_id.encode("utf-8"),
        user_name=agent_id,
        attestation="none",
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    session["webauthn"]["register_challenge"] = opts.challenge
    return opts

@router.post("/register/verify")
def register_verify(body: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    sid, session = _must_session(identity)

    challenge = session["webauthn"].get("register_challenge")
    if not challenge:
        raise HTTPException(400, "No register challenge in session")

    cred = RegistrationCredential.parse_obj(body)

    verification = verify_registration_response(
        credential=cred,
        expected_challenge=challenge,
        expected_rp_id=RP_ID,
        expected_origin=f"http://{RP_ID}:3001",  # your Vite origin
        require_user_verification=False,
    )

    # store credential
    db.add(WebAuthnCredential(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        credential_id=verification.credential_id,
        public_key=verification.credential_public_key,
        sign_count=verification.sign_count,
    ))
    db.commit()

    session["webauthn"].pop("register_challenge", None)
    return {"ok": True, "message": "Fingerprint/Passkey enrolled"}

# ---------- AUTH (step-up) ----------

@router.post("/auth/options")
def auth_options(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    sid, session = _must_session(identity)

    creds = db.query(WebAuthnCredential).filter(WebAuthnCredential.agent_id == agent_id).all()
    if not creds:
        raise HTTPException(400, "No fingerprint/passkey enrolled. Register first.")

    allow = [
        PublicKeyCredentialDescriptor(
            type=PublicKeyCredentialType.PUBLIC_KEY,
            id=c.credential_id,
        )
        for c in creds
    ]

    opts = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    session["webauthn"]["auth_challenge"] = opts.challenge
    return opts

@router.post("/auth/verify")
def auth_verify(body: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    sid, session = _must_session(identity)

    challenge = session["webauthn"].get("auth_challenge")
    if not challenge:
        raise HTTPException(400, "No auth challenge in session")

    cred = AuthenticationCredential.parse_obj(body)

    # find stored credential
    stored = db.query(WebAuthnCredential).filter(
        WebAuthnCredential.agent_id == agent_id,
        WebAuthnCredential.credential_id == cred.raw_id
    ).first()

    # Some clients send id/rawId differently. If not found, try match by "id"
    if not stored:
        stored = db.query(WebAuthnCredential).filter(
            WebAuthnCredential.agent_id == agent_id,
            WebAuthnCredential.credential_id == cred.id
        ).first()

    if not stored:
        raise HTTPException(400, "Credential not registered")

    verification = verify_authentication_response(
        credential=cred,
        expected_challenge=challenge,
        expected_rp_id=RP_ID,
        expected_origin=f"http://{RP_ID}:3001",
        credential_public_key=stored.public_key,
        credential_current_sign_count=stored.sign_count,
        require_user_verification=False,
    )

    stored.sign_count = verification.new_sign_count
    db.commit()

    session["webauthn"].pop("auth_challenge", None)

    # ✅ mark step-up done and bump trust
    set_step_up(sid, True)
    bump_trust(sid, 0.08)

    return {"ok": True, "message": "Fingerprint verified (step-up complete)"}