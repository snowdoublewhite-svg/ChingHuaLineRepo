const express = require("express");
const app = express();

// 先把 raw body 留下來，避免某些情況解析出問題
app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf?.toString("utf8") || ""; }
}));

// 任何 request 都先打一行 log（最重要）
app.use((req, res, next) => {
  console.log(`[REQ] ${req.method} ${req.path}`);
  next();
});

app.get("/", (req, res) => res.status(200).send("OK"));

// 讓你用瀏覽器直接驗證 /webhook 有沒有到這個服務
app.get("/webhook", (req, res) => {
  console.log("[GET /webhook] hit");
  res.status(200).send("WEBHOOK OK");
});

app.post("/webhook", (req, res) => {
  console.log("[POST /webhook] body:", JSON.stringify(req.body));
  // 如果解析不到 body，也把 rawBody 印出來
  if (!req.body || Object.keys(req.body).length === 0) {
    console.log("[POST /webhook] rawBody:", req.rawBody);
  }
  return res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Listening on ${PORT}`));
