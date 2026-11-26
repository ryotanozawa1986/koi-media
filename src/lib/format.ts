const dateFormat = new Intl.DateTimeFormat('ja-JP', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  timeZone: 'Asia/Tokyo',
});

const isoFormat = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  timeZone: 'Asia/Tokyo',
});

export function formatDate(date: Date): string {
  return dateFormat.format(date);
}

export function isoDate(date: Date): string {
  return isoFormat.format(date);
}
