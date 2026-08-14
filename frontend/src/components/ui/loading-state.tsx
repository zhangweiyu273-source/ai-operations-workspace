export function LoadingState({ label = "加载中" }: { label?: string }) {
  return <div className="loading-state" role="status"><span />{label}</div>;
}
