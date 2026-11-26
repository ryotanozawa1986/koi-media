export function totalPagesOf(count: number, perPage: number): number {
  if (count <= 0) return 1;
  return Math.ceil(count / perPage);
}

export function paginate<T>(items: readonly T[], page: number, perPage: number): {
  page: number;
  totalPages: number;
  items: T[];
} {
  const totalPages = totalPagesOf(items.length, perPage);
  const current = Math.min(Math.max(page, 1), totalPages);
  const start = (current - 1) * perPage;
  return {
    page: current,
    totalPages,
    items: items.slice(start, start + perPage),
  };
}
