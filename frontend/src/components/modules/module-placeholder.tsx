import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";

export function ModulePlaceholder({ title, description }: { title: string; description: string }) {
  return (
    <section>
      <PageHeader title={title} description={description} />
      <EmptyState title="功能建设中" description="基础路由已经就绪，业务能力将在后续任务中逐步开放。" />
    </section>
  );
}
