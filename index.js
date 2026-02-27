const express = require("express");
const app = express();

app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf?.toString("utf8") || ""; }
}));

// 任何 request 都記錄
app.use((req, res, next) => {
  console.log(`[REQ] ${req.method} ${req.path}`);
  next();
});

app.get("/", (req, res) => res.status(200).send("OK"));

app.get("/webhook", (req, res) => {
  console.log("[GET /webhook] hit");
  res.status(200).send("WEBHOOK OK");
});

app.post("/webhook", (req, res) => {
  console.log("[POST /webhook] body:", JSON.stringify(req.body));
  if (!req.body || Object.keys(req.body).length === 0) {
    console.log("[POST /webhook] rawBody:", req.rawBody);
  }
  return res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Listening on ${PORT}`));
