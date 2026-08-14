import { existsSync } from "node:fs";

if (existsSync(".next/lock")) {
  console.error("检测到 .next/lock：已有 Next.js dev/build 进程正在使用构建目录。请先停止该进程；确认无进程后可运行 npm run build:clean。");
  process.exit(1);
}

if (process.env.NODE_OPTIONS) {
  console.log("检测到系统 NODE_OPTIONS；本项目不依赖该变量，将按 Node.js 当前环境继续构建。");
}
