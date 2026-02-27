const express = require("express");
const app = express();

// LINE 會用 POST 打 webhook，內容是 JSON
app.use(express.json());

// 健康檢查：用瀏覽器打開網址可以看到 OK
app.get("/", (req, res) => res.status(200).send("OK"));

// 你的 webhook endpoint（等下 LINE 後台要填這個）
app.post("/webhook", (req, res) => {
  // 先把收到的東西印出來（Render Logs 會看到）
  console.log("Webhook body:", JSON.stringify(req.body));

  // LINE 要你回 200，表示你收到了
  return res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Listening on ${PORT}`));
