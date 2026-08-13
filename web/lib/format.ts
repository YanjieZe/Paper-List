export function formatDate(value: string | Date | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function formatCost(value: string | number | null) {
  return `$${Number(value ?? 0).toFixed(3)}`;
}
