import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

export default function AgentLogin() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [decisionId, setDecisionId] = useState("");
  const [step, setStep] = useState(1);

  const sendOtp = async () => {
    const res = await api.post("/agent/auth/login", { email, password });
    setDecisionId(res.data.decision_id);
    setStep(2);
    alert("OTP sent (or printed in backend console)");
  };

  const verifyOtp = async () => {
    const res = await api.post("/agent/auth/verify-otp", {
      email,
      otp,
      decision_id: decisionId,
    });

    localStorage.setItem("token", res.data.access_token);
    nav("/agent/dashboard"); // ✅ redirect
  };
  localStorage.setItem("token", res.data.access_token);
    console.log("TOKEN SAVED:", res.data.access_token);

  return (
    <div>
      {step === 1 ? (
        <>
          <input placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e)=>setPassword(e.target.value)} />
          <button onClick={sendOtp}>Send OTP</button>
        </>
      ) : (
        <>
          <input placeholder="OTP" value={otp} onChange={(e)=>setOtp(e.target.value)} />
          <button disabled={!decisionId || !otp} onClick={verifyOtp}>Verify OTP</button>
        </>
      )}
    </div>
  );
}