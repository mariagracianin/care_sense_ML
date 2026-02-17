from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

last_state = {
    "state": "unknown",
    "score": None,
    "timestamp": None
}

@app.post("/state")
def receive_state():
    data = request.get_json(silent=True) or {}
    state = data.get("state")
    score = data.get("score")

    if not state:
        return jsonify({"ok": False, "error": "Missing 'state'"}), 400

    last_state["state"] = state
    last_state["score"] = score
    last_state["timestamp"] = datetime.now().isoformat(timespec="seconds")

    print("Nuevo estado recibido:", last_state, flush=True)
    return jsonify({"ok": True, **last_state})

@app.get("/last")
def get_last():
    return jsonify({"ok": True, **last_state})

@app.get("/")
def home():
    return """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>IMU State Monitor</title>
  <style>
    :root{
      --bg0:#070a0f;
      --bg1:#0b1220;
      --stroke:#203044;
      --text:#eaf2ff;
      --muted:#9fb2c7;

      --ok:#20c997;
      --warn:#ffd166;
      --fall:#ff3b3b;
      --unk:#7b8ba1;
    }

    *{box-sizing:border-box}
    body{
      margin:0;
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:32px;
      color:var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      background:
        radial-gradient(900px 500px at 15% 15%, rgba(80,230,255,.10), transparent 55%),
        radial-gradient(900px 500px at 85% 85%, rgba(32,201,151,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }

    .card{
      width:min(720px, 100%);
      position:relative;
      border:1px solid var(--stroke);
      background:linear-gradient(180deg, rgba(18,27,44,.86), rgba(10,16,28,.86));
      border-radius:22px;
      padding:22px 22px 18px;
      box-shadow: 0 18px 50px rgba(0,0,0,.45);
      backdrop-filter: blur(10px);
      overflow:hidden;
    }

    .card:before{
      content:"";
      position:absolute;
      inset:-2px;
      background:
        radial-gradient(520px 220px at 20% 10%, rgba(80,230,255,.18), transparent 60%),
        radial-gradient(520px 220px at 80% 0%, rgba(0,120,212,.18), transparent 55%),
        radial-gradient(520px 220px at 75% 95%, rgba(32,201,151,.14), transparent 55%);
      pointer-events:none;
      filter:saturate(120%);
    }

    .pulse{
      position:absolute;
      inset:0;
      pointer-events:none;
      border-radius:22px;
      border:1px solid transparent;
      opacity:0;
    }

    .top{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      position:relative;
      z-index:1;
    }

    .title{
      display:flex;
      align-items:center;
      gap:10px;
      font-weight:800;
      letter-spacing:.2px;
      opacity:.95;
    }

    .dot{
      width:12px;height:12px;border-radius:50%;
      background:var(--unk);
      box-shadow:0 0 0 4px rgba(123,139,161,.14);
      transition: .25s ease;
    }

    .pill{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:7px 12px;
      border-radius:999px;
      border:1px solid var(--stroke);
      background:rgba(9,14,24,.6);
      color:var(--muted);
      font-size:12px;
      letter-spacing:.3px;
      text-transform:uppercase;
      user-select:none;
    }

    .pill .miniDot{
      width:8px;height:8px;border-radius:50%;
      background:var(--unk);
      opacity:.9;
      transition:.25s ease;
    }

    .bigState{
      position:relative;
      z-index:1;
      margin-top:14px;
      font-size:64px;
      line-height:1;
      font-weight:950;
      letter-spacing:.5px;
      text-transform:lowercase;
    }

    .subgrid{
      position:relative;
      z-index:1;
      margin-top:14px;
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:12px;
    }

    .kv{
      border:1px solid var(--stroke);
      border-radius:18px;
      padding:12px 14px;
      background:rgba(7,11,18,.45);
    }
    .k{
      color:var(--muted);
      font-size:12px;
      letter-spacing:.3px;
      text-transform:uppercase;
      margin-bottom:6px;
    }
    .v{
      font-weight:800;
      font-size:18px;
    }

    code{
      background:#132033;
      border:1px solid var(--stroke);
      padding:2px 6px;
      border-radius:8px;
      color:#cfe6ff;
    }

    .api{
      position:relative;
      z-index:1;
      margin-top:14px;
      display:flex;
      flex-wrap:wrap;
      gap:10px;
      color:var(--muted);
      font-size:13px;
      opacity:.95;
    }

    /* ====== Dynamic state styling ====== */
    .ok .dot{ background:var(--ok); box-shadow:0 0 0 4px rgba(32,201,151,.16); }
    .ok .pill .miniDot{ background:var(--ok); }
    .ok .bigState{ text-shadow: 0 0 22px rgba(32,201,151,.22); }

    .warn .dot{ background:var(--warn); box-shadow:0 0 0 4px rgba(255,209,102,.16); }
    .warn .pill .miniDot{ background:var(--warn); }
    .warn .bigState{ text-shadow: 0 0 22px rgba(255,209,102,.18); }

    .fall .dot{ background:var(--fall); box-shadow:0 0 0 4px rgba(255,59,59,.18); }
    .fall .pill .miniDot{ background:var(--fall); }
    .fall .bigState{ color:#ffd9d9; text-shadow: 0 0 26px rgba(255,59,59,.30); }
    .fall .card{
      box-shadow: 0 20px 70px rgba(255,59,59,.12), 0 18px 50px rgba(0,0,0,.55);
    }

    .fall .pulse{
      border-color: rgba(255,59,59,.35);
      box-shadow: 0 0 30px rgba(255,59,59,.35);
      animation: pulse 1.1s infinite;
      opacity:1;
    }

    @keyframes pulse{
      0%   { transform:scale(1);   opacity:.85; }
      70%  { transform:scale(1.02);opacity:.25; }
      100% { transform:scale(1);   opacity:.75; }
    }

    .fall .bigState{
      animation: shake .22s ease-in-out 1;
    }
    @keyframes shake{
      0%{ transform:translateX(0); }
      25%{ transform:translateX(-4px); }
      50%{ transform:translateX(4px); }
      75%{ transform:translateX(-2px); }
      100%{ transform:translateX(0); }
    }

    @media (max-width: 720px){
      .bigState{ font-size:56px; }
      .subgrid{ grid-template-columns:1fr; }
    }
  </style>
</head>

<body>
  <div class="card" id="card">
    <div class="pulse"></div>

    <div class="top">
      <div class="title">
        <span class="dot"></span>
        <span>IMU State Monitor</span>
      </div>

      <div class="pill">
        <span class="miniDot"></span>
        <span id="statusText">conectando</span>
      </div>
    </div>

    <div id="state" class="bigState">unknown</div>

    <div class="subgrid">
      <div class="kv">
        <div class="k">score</div>
        <div class="v" id="score">—</div>
      </div>

      <div class="kv">
        <div class="k">timestamp</div>
        <div class="v" id="ts">—</div>
      </div>
    </div>

    <div class="api">
      <span>GET <code>/last</code></span>
      <span>POST <code>/state</code></span>
      <span style="margin-left:auto; opacity:.8" id="clock">—</span>
    </div>
  </div>

<script>
  const card = document.getElementById("card");
  const statusText = document.getElementById("statusText");

  function classifyState(raw) {
    const s = String(raw ?? "unknown").trim().toLowerCase();

    // Caída (ROJO)
    if (["fall","fallen","falling","caida","caída","impact","impacto"].includes(s)) return "fall";

    // Warning (amarillo)
    if (s.includes("near") || s.includes("warn") || s.includes("risk")) return "warn";

    // Normal (verde)
    if (["idle","standing","walking","running","normal","ok"].includes(s)) return "ok";

    return "unk";
  }

  function setUI(data, online=true){
    const rawState = data.state ?? "unknown";
    const klass = classifyState(rawState);

    card.classList.remove("ok","warn","fall","unk");
    card.classList.add(klass);

    document.getElementById("state").textContent = String(rawState).toLowerCase();

    const sc = data.score;
    document.getElementById("score").textContent =
      (sc === null || sc === undefined || sc === "") ? "—" : Number(sc).toFixed(4);

    document.getElementById("ts").textContent = data.timestamp ?? "—";

    statusText.textContent = online ? "live" : "offline";
  }

  async function refresh() {
    try {
      const r = await fetch("/last", { cache: "no-store" });
      const data = await r.json();
      setUI(data, true);
    } catch (e) {
      setUI({state:"unknown", score:null, timestamp:null}, false);
    }
  }

  function tickClock(){
    const d = new Date();
    document.getElementById("clock").textContent = d.toLocaleTimeString();
  }

  tickClock();
  setInterval(tickClock, 1000);

  refresh();
  setInterval(refresh, 300);
</script>

</body>
</html>
"""

if __name__ == "__main__":
    # IMPORTANTE: sin debug para evitar el reloader duplicado
    app.run(host="127.0.0.1", port=5000, debug=False)