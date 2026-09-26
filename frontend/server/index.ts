import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = createServer(app);
  const backendRoutes = ["/api", "/register", "/login", "/logout", "/auth", "/dashboard", "/policy/share"];
  const backendBaseUrl = (process.env.BACKEND_BASE_URL || "http://127.0.0.1:5000").replace(/\/+$/, "");

  app.use(createProxyMiddleware({
    target: backendBaseUrl,
    changeOrigin: true,
    pathFilter: (pathname) => backendRoutes.some((route) => pathname === route || pathname.startsWith(`${route}/`)),
    on: {
      error: (_error, _request, response) => {
        if ("writeHead" in response) {
          if (response.headersSent) return;
          response.writeHead(502, { "Content-Type": "application/json" });
          response.end(JSON.stringify({ error: "Backend service unavailable." }));
        } else {
          response.destroy();
        }
      },
    },
  }));

  // Serve static files from dist/public in production
  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");

  app.use(express.static(staticPath));

  // Handle client-side routing - serve index.html for all routes
  app.get("*", (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  const port = process.env.PORT || 3000;

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
