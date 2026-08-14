import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";

export default function Home() {
  return (
    <section>
      <PageHeader title="运营首页" description="统一查看运营工作状态与系统能力。" />
      <div className="home-grid">
        <Card className="welcome-card">
          <span className="eyebrow">AI OPERATIONS WORKBENCH</span>
          <h2>数据底座已就绪</h2>
          <p>阶段 B 正在建立可持续扩展的数据结构和全局工作台框架。</p>
        </Card>
        <Card className="status-card">
          <span className="system-dot" />
          <div><strong>基础服务正常</strong><p>前端、API 与 PostgreSQL 已连接</p></div>
        </Card>
      </div>
    </section>
  );
}
