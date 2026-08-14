import { rmSync } from "node:fs";

rmSync(".next", { recursive: true, force: true });
console.log("已清理前端构建缓存 .next。请确保没有并发运行的 next dev/build 进程。");
